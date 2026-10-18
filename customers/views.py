from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import mimetypes

from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from .models import Customer
from .forms import CustomerCreateForm



User = get_user_model()

def get_profile(user):
    try:
        return user.profile
    except UserProfile.DoesNotExist:
        raise PermissionDenied("Your account has no assigned role.")


def home(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin:index")

    profile = get_profile(request.user)

    if profile.role == UserProfile.Role.MAKER:
        return redirect("maker_dashboard")

    if profile.role == UserProfile.Role.CHECKER:
        return redirect("checker_dashboard")

    raise PermissionDenied("Unsupported user role.")

@login_required
def customer_create(request):
    profile = get_profile(request.user)

    if profile.role != UserProfile.Role.MAKER:
        raise PermissionDenied("Only Makers can submit customers.")

    if request.method == "POST":
        form = CustomerCreateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            customer = form.save(commit=False)
            customer.uploaded_by = request.user
            customer.status = Customer.Status.PENDING
            customer.save()

            messages.success(
                request,
                "Customer submitted successfully for review.",
            )
            return redirect("maker_dashboard")
    else:
        form = CustomerCreateForm()

    return render(
        request,
        "customers/customer_create.html",
        {"form": form},
    )


def maker_customer_queryset(user):
    return Customer.objects.filter(uploaded_by=user)


def checker_customer_queryset(profile):
    maker_user_ids = UserProfile.objects.filter(
        role=UserProfile.Role.MAKER,
        assigned_checker=profile,
    ).values_list("user_id", flat=True)

    return Customer.objects.filter(uploaded_by_id__in=maker_user_ids)


def filter_customers(request, queryset, *, allow_maker_search=False):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    maker = request.GET.get("maker", "").strip()

    if query:
        matching = Q(full_name__icontains=query) | Q(email__icontains=query)
        

        if allow_maker_search:
                matching_user_ids = list(
                    User.objects.filter(
                        username__icontains=query
                    ).values_list("pk", flat=True)
                )

                matching_maker_ids = list(
                    UserProfile.objects.filter(
                        role=UserProfile.Role.MAKER,
                        user_id__in=matching_user_ids,
                    ).values_list("user_id", flat=True)
                )

                matching |= Q(uploaded_by_id__in=matching_maker_ids)

        queryset = queryset.filter(matching)

    valid_statuses = {choice[0] for choice in Customer.Status.choices}
    if status in valid_statuses:
        queryset = queryset.filter(status=status)

    if allow_maker_search and maker:
        queryset = queryset.filter(uploaded_by_id=maker)

    return queryset, query, status, maker


@login_required
def maker_dashboard(request):
    profile = get_profile(request.user)

    if profile.role != UserProfile.Role.MAKER:
        raise PermissionDenied("Only Makers can access this page.")

    all_customers = maker_customer_queryset(request.user)
    customers, query, status, _ = filter_customers(
        request,
        all_customers,
    )

    context = {
        "customers": customers,
        "total_count": all_customers.count(),
        "pending_count": all_customers.filter(
            status=Customer.Status.PENDING
        ).count(),
        "approved_count": all_customers.filter(
            status=Customer.Status.APPROVED
        ).count(),
        "declined_count": all_customers.filter(
            status=Customer.Status.DECLINED
        ).count(),
        "query": query,
        "selected_status": status,
        "status_choices": Customer.Status.choices,
    }

    return render(request, "customers/maker_dashboard.html", context)


@login_required
def maker_customer_detail(request, customer_id):
    profile = get_profile(request.user)

    if profile.role != UserProfile.Role.MAKER:
        raise PermissionDenied("Only Makers can access this page.")

    customer = get_object_or_404(
        maker_customer_queryset(request.user),
        pk=customer_id,
    )

    return render(
        request,
        "customers/maker_customer_detail.html",
        {"customer": customer},
    )


@login_required
def checker_dashboard(request):
    profile = get_profile(request.user)

    if profile.role != UserProfile.Role.CHECKER:
        raise PermissionDenied("Only Checkers can access this page.")

    all_customers = checker_customer_queryset(profile)
    customers, query, status, maker = filter_customers(
        request,
        all_customers,
        allow_maker_search=True,
    )

    makers = UserProfile.objects.filter(
        role=UserProfile.Role.MAKER,
        assigned_checker=profile,
    ).select_related("user")

    context = {
        "customers": customers,
        "total_count": all_customers.count(),
        "pending_count": all_customers.filter(
            status=Customer.Status.PENDING
        ).count(),
        "approved_count": all_customers.filter(
            status=Customer.Status.APPROVED
        ).count(),
        "declined_count": all_customers.filter(
            status=Customer.Status.DECLINED
        ).count(),
        "query": query,
        "selected_status": status,
        "selected_maker": maker,
        "status_choices": Customer.Status.choices,
        "makers": makers,
    }

    return render(request, "customers/checker_dashboard.html", context)


@login_required
def checker_customer_detail(request, customer_id):
    profile = get_profile(request.user)

    if profile.role != UserProfile.Role.CHECKER:
        raise PermissionDenied("Only Checkers can access this page.")

    customer = get_object_or_404(
        checker_customer_queryset(profile),
        pk=customer_id,
    )

    return render(
        request,
        "customers/checker_customer_detail.html",
        {"customer": customer},
    )


@login_required
def customer_file(request, customer_id, file_type):
    profile = get_profile(request.user)

    if profile.role == UserProfile.Role.MAKER:
        queryset = maker_customer_queryset(request.user)
    elif profile.role == UserProfile.Role.CHECKER:
        queryset = checker_customer_queryset(profile)
    else:
        raise PermissionDenied

    customer = get_object_or_404(queryset, pk=customer_id)

    if file_type not in ("photo", "resume"):
        raise Http404("File not found.")

    uploaded_file = getattr(customer, file_type, None)

    if not uploaded_file:
        raise Http404("File not found.")

    try:
        uploaded_file.open("rb")
        content_type, _ = mimetypes.guess_type(uploaded_file.name)

        response = FileResponse(
            uploaded_file,
            content_type=content_type or "application/octet-stream",
        )

        if file_type == "resume":
            response["Content-Disposition"] = "attachment"

        return response

    except (OSError, ValueError):
        raise Http404("File could not be opened.")


@login_required
@require_POST
def review_customer(request, customer_id):
    profile = get_profile(request.user)

    if profile.role != UserProfile.Role.CHECKER:
        raise PermissionDenied("Only Checkers can review customers.")

    decision = request.POST.get("decision")

    if decision not in (
        Customer.Status.APPROVED,
        Customer.Status.DECLINED,
    ):
        raise PermissionDenied("Invalid review decision.")

    customer = get_object_or_404(
        checker_customer_queryset(profile).filter(
            pk=customer_id,
            status=Customer.Status.PENDING,
        )
    )

    customer.status = decision
    customer.reviewed_by = request.user
    customer.reviewed_at = timezone.now()
    customer.save(
        update_fields=["status", "reviewed_by", "reviewed_at"]
    )

    messages.success(
        request,
        f"Customer {customer.full_name} was {decision.lower()}.",
    )

    return redirect("checker_customer_detail", customer_id=customer.pk)


@staff_member_required
def media_diagnostic(request):
    results = []

    for customer in Customer.objects.all():
        item = {
            "customer_id": str(customer.pk),
            "photo_name": customer.photo.name if customer.photo else None,
            "resume_name": customer.resume.name if customer.resume else None,
            "photo_exists": (
                customer.photo.storage.exists(customer.photo.name)
                if customer.photo else False
            ),
            "resume_exists": (
                customer.resume.storage.exists(customer.resume.name)
                if customer.resume else False
            ),
        }
        results.append(item)

    return JsonResponse({
        "media_root": str(settings.MEDIA_ROOT),
        "customers": results,
    })