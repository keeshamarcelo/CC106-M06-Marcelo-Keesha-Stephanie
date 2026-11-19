from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import StudentForm
from .models import Student


def student_registration(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registration_success')
    else:
        form = StudentForm()

    return render(
        request,
        'registration/registration.html',
        {'form': form},
    )


def registration_success(request):
    return render(request, 'registration/success.html')


def staff_check(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(staff_check, login_url='staff_login')
def staff_dashboard(request):
    total_students = Student.objects.count()
    male_students = Student.objects.filter(gender='Male').count()
    female_students = Student.objects.filter(gender='Female').count()

    male_percent = (
        male_students / total_students * 100
        if total_students > 0 else 0
    )
    female_percent = (
        female_students / total_students * 100
        if total_students > 0 else 0
    )

    query = request.GET.get('q', '').strip()
    students = Student.objects.all().order_by('last_name', 'first_name')
    if query:
        students = students.filter(
            Q(student_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    context = {
        'total_students': total_students,
        'male_students': male_students,
        'female_students': female_students,
        'male_percent': male_percent,
        'female_percent': female_percent,
        'students': students,
        'query': query,
    }
    return render(request, 'registration/dashboard.html', context)


def staff_login(request):
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ''

    if request.user.is_authenticated and request.user.is_staff:
        return redirect(next_url or 'staff_dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect(next_url or 'staff_dashboard')

        error = 'Invalid staff username or password.'

    return render(
        request,
        'registration/login.html',
        {
            'error': error,
            'next': next_url,
        },
    )


@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')


def student_list(request):
    query = request.GET.get('q', '').strip()
    students = Student.objects.all().order_by('last_name', 'first_name')
    if query:
        students = students.filter(
            Q(student_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    return render(
        request,
        'registration/student_list.html',
        {'students': students, 'query': query},
    )


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(
        request,
        'registration/student_detail.html',
        {'student': student},
    )


def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student record created successfully.')
            return redirect('student_list')
    else:
        form = StudentForm()

    return render(
        request,
        'registration/student_form.html',
        {'form': form, 'page_title': 'Register Student'},
    )


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student record updated successfully.')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        'registration/student_form.html',
        {
            'form': form,
            'page_title': 'Update Student',
            'student': student,
        },
    )


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student record deleted successfully.')
        return redirect('student_list')

    return render(
        request,
        'registration/student_confirm_delete.html',
        {'student': student},
    )