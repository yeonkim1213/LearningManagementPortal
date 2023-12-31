from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseBadRequest,HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from . import models
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.
@login_required
def assignments(request):
    allAssignments = models.Assignment.objects.all()
    return render(request, 'assignments.html', {'assignments': allAssignments})

def is_student(user):
    return user.groups.filter(name="Students").exists()

def is_ta(user):
    return user.groups.filter(name="Teaching Assistants").exists() or user.is_superuser

@login_required
def assignment(request, assignment_id):
    
    assignment404 = get_object_or_404(models.Assignment, pk=assignment_id)

    assignmentInfo = {
        'assignment': assignment404,
        'is_ta': is_ta(request.user),
        'is_student': is_student(request.user),
    }
     
    if is_ta(request.user) or request.user.is_superuser:
        assignmentInfo.update({
            'submissionsTotal': models.Submission.objects.filter(assignment=assignment404).count(),
            'totalStudents': models.Group.objects.get(name="Students").user_set.count(),
            'submissionsAssigned': models.Submission.objects.filter(assignment=assignment404, grader__username=request.user).count(),
        })

    elif is_student(request.user):
        try:
            submission = models.Submission.objects.get(assignment=assignment404, author=request.user)
            filename = submission.file.name.split('/')[-1]

            if submission.score is not None:
                assignmentPoint = submission.score/assignment404.points*100
                assignmentPoint = round(assignmentPoint, 2)
                intScore = (int)(submission.score)
                assignmentInfo['submissionStatus'] = f"Your submission, {filename}, received {intScore}/{assignment404.points} points ({assignmentPoint}%)"
            elif assignment404.deadline > timezone.now():
                assignmentInfo['submissionStatus'] = f"Your current submission is {filename}."
            else:
                assignmentInfo['submissionStatus'] = f"Your submission, {filename}, is being graded."

        except models.Submission.DoesNotExist:
            if assignment404.deadline > timezone.now():
                assignmentInfo['submissionStatus'] = "No current submission."
            else:
                assignmentInfo['submissionStatus'] = "You did not submit this assignment and received 0 points."

    return render(request, 'index.html', assignmentInfo)

@login_required
@user_passes_test(is_ta)
def submissions(request, assignment_id):
    assignment404 = get_object_or_404(models.Assignment, pk=assignment_id)

    if request.user.is_superuser:
        submissions = models.Submission.objects.filter(assignment=assignment404).order_by('author__username')
    elif is_ta(request.user):
        submissions = models.Submission.objects.filter(assignment=assignment404, grader=request.user).order_by('author__username')
    else:
        submissions: None
    return render(request, "submissions.html", {'submissions': submissions, 'assignment': assignment404})

@login_required
def profile(request):
    assignmentGrade = {}
    assignmentGrade['is_ta'] = is_ta(request.user)

    if request.user.is_superuser:
        assignmentGrading = []

        for assignment in models.Assignment.objects.all():
            assignedStudents = models.Submission.objects.filter(assignment=assignment).count()
            graded = models.Submission.objects.filter(assignment=assignment, score__isnull=False).count()

            assignmentGrading.append({
                    'assignment': assignment,
                    'assignedStudents': assignedStudents,
                    'graded': graded
            })

        assignmentGrade['assignmentGrading'] = assignmentGrading

    elif is_ta(request.user):
        assignmentGrading = []
        for assignment in models.Assignment.objects.all():
            assignedStudents = models.Submission.objects.filter(assignment=assignment, grader=request.user).count()
            graded = models.Submission.objects.filter(assignment=assignment, grader=request.user, score__isnull=False).count()

            assignmentGrading.append({
                    'assignment': assignment,
                    'assignedStudents': assignedStudents,
                    'graded': graded
            })

        assignmentGrade['assignmentGrading'] = assignmentGrading

    elif is_student(request.user):
            studentAssignments = []

            for assignment in models.Assignment.objects.all():
                try:
                    submission = models.Submission.objects.get(assignment=assignment, author=request.user)

                    if submission.score is not None:
                        percentage = submission.score / assignment.points * 100
                        status = "Graded"
    
                    else:
                        status = "Ungraded"
                        percentage = None

                except models.Submission.DoesNotExist:

                    if assignment.deadline > timezone.now():
                        status = "Not due"
                        percentage = None
                    
                    else:
                        status = "Missing"
                        percentage = 0 

                studentAssignments.append({
                    'assignment': assignment,
                    'status': status,
                    'percentage': percentage
                })
         
            current_grade = compute_current_grade(studentAssignments)
            assignmentGrade['studentAssignments'] = studentAssignments
            assignmentGrade['current_grade'] = current_grade

    return render(request, "profile.html", assignmentGrade)

def compute_current_grade(studentAssignments):
    earnedPoints = 0
    availablePoints = 0

    for data in studentAssignments:
        if data['status'] == 'Graded':
            availablePoints += data['assignment'].weight
            earnedPoints += data['assignment'].weight * data['percentage'] / 100

        elif data['status'] == 'Missing':
             availablePoints += data['assignment'].weight

    if availablePoints == 0:
        return 100 
        
    finalGrade = (earnedPoints / availablePoints) * 100

    return round(finalGrade, 2)


def login_form(request):
   
    next_url = request.GET.get('next', '/profile/')

    if request.method == "POST":
        username = request.POST.get("username", '')
        password = request.POST.get("password", '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.POST.get('next', '/profile/'))
        else:
            return render(request, 'login.html', {'next': next_url, 'error': 'Username and password do not match'})
    else:
        return render(request, 'login.html', {'next': next_url})

def logout_form(request):
    logout(request)
    return redirect('/profile/login/')

@login_required
@user_passes_test(is_ta)
def grade(request, assignment_id):

    get_object_or_404(models.Assignment, pk = assignment_id)

    if request.method == 'POST':
        
        submissions_post = []

        for input in request.POST:

            if input.startswith('grade-'):
               
                try:
                    input_id =  int(input.split('-')[1])
                    submission_id = input_id
                    submission = get_object_or_404(models.Submission, id=submission_id)

                    if submission.assignment.id != assignment_id:
                        raise Http404

                    try:
                        score = float(request.POST[input])

                    except ValueError:
                        score = None

                    submission.score = score
                    submissions_post.append(submission)

                except ValueError:
                    raise Http404("The value is error")

        if submissions_post:
            models.Submission.objects.bulk_update( submissions_post, ['score'])

        return redirect('submissions', assignment_id=assignment_id)
    else:
        raise Http404
    
def pick_grader(assignment):
    TAGroup = models.Group.objects.get(name='Teaching Assistants')
    fewestAssigned = TAGroup.user_set.annotate(total_assigned = Count('submission', filter=Q(submission__assignment=assignment,  submission__score__isnull=True))).order_by('total_assigned')

    return fewestAssigned.first()
    
@login_required
@user_passes_test(is_student)
def submit(request, assignment_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Not POST")
     
    assignment404 = get_object_or_404(models.Assignment, pk=assignment_id)

    if assignment404.deadline < timezone.now():
        return HttpResponseBadRequest("No longer accepting assignment.")

    submitted = request.FILES.get('file')

    if not submitted:
        return HttpResponseBadRequest("No file was submitted.")

    submission, created = models.Submission.objects.get_or_create(
        assignment = assignment404,
        author = request.user,
        defaults={'grader': pick_grader(assignment404), 'file': submitted}
    )

    if not created:
        submission.file = submitted
        submission.save()

    return redirect('index', assignment_id=assignment404.id)

@login_required
def show_upload(request, filename):
    
    # submission = models.Submission.objects.get(file='uploads/' + filename)
    
    # if request.user != submission.author and request.user != submission.grader and not request.user.is_superuser :
    #     raise PermissionDenied

    # with submission.file.open() as fd:
    #     response = HttpResponse(fd)
    #     response["Content-Disposition"] = \
    #         f'attachment; filename="{submission.file.name}"'
         return 0