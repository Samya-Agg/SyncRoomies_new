from django.shortcuts import render,HttpResponse,redirect
from .models import *
import pandas as pd
from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, FloatField
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import student,Student_choices
from .models import profile as Profile
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import numpy as np

# Create your views here.

def find_matches(request, student_id):
    try:
        target = Student_choices.objects.get(student_id=student_id)
    except Student_choices.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)

    # Filter by same gender
    candidates = Student_choices.objects.filter(gender=target.gender).exclude(student_id=student_id)

    if len(candidates) == 0:
        return JsonResponse({"message": "No matching candidates for this gender."})

    # Convert to DataFrame
    data = []
    for s in candidates:
        data.append([
            s.student_id,
            s.extraversion, s.agreeableness, s.conscientiousness,
            s.neuroticism, s.openness
        ])

    df = pd.DataFrame(data, columns=[
        "student_id", "Ext", "Agr", "Con", "Neu", "Opn"
    ])

    target_vec = np.array([
        target.extraversion, target.agreeableness, target.conscientiousness,
        target.neuroticism, target.openness
    ]).reshape(1, -1)

    # Scale data
    scaler = StandardScaler()
    X = df[["Ext", "Agr", "Con", "Neu", "Opn"]]
    X_scaled = scaler.fit_transform(X)
    target_scaled = scaler.transform(target_vec)

    # KNN
    k = min(5, len(df))  # top 5 matches
    knn = NearestNeighbors(n_neighbors=k, metric='euclidean')
    knn.fit(X_scaled)
    distances, indices = knn.kneighbors(target_scaled)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        sid = df.iloc[idx]["student_id"]
        student_obj = Student_choices.objects.get(student_id=sid)

        results.append({
            "student_id": sid,
            "name": student_obj.name,
            "distance": float(dist),
            "traits": {
                "Extraversion": student_obj.extraversion,
                "Agreeableness": student_obj.agreeableness,
                "Conscientiousness": student_obj.conscientiousness,
                "Neuroticism": student_obj.neuroticism,
                "Openness": student_obj.openness,
            }
        })

    return JsonResponse({"target": target.name, "matches": results})


def homepage(request):
    return render(request,'index.html')

def register_page(request):
    if request.method=="POST":
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('username')
        password=request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request,'Username already taken.',extra_tags='register')
            return redirect('/register/')

        user=User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

        user.set_password(password)
        user.save()
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request,"Account created successfully")
            return redirect('/profile/')
        else:
            messages.error(request, "Failed to login automatically",extra_tags='register')
            return redirect('/login/')

    return render(request,'register.html')


def login_page(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request,'Invalid Username',extra_tags='login')
            return redirect('/login/')
        user=authenticate(username=username,password=password)

        if user is None:
            messages.error(request,'Invalid Password',extra_tags='login')
            return redirect('/login/')
        
        login(request,user)

        # Redirect Logic Fix
        # If profile missing → Profile page
        if not Profile.objects.filter(user=user).exists():
            return redirect('/profile/')

        # If BFI already done → results
        if Student_choices.objects.filter(student_id=user).exists():
            return redirect('/results/')

        # Else → go to BFI
        return redirect('/bfi/')

    return render(request,'login.html')



def index1(request):
    # This view is unused now; redirect to BFI always
    return redirect('/bfi/')


def submit_bfi(request):
    user = request.user

    # Prevent duplicate submissions
    if Student_choices.objects.filter(student_id=user).exists():
        return redirect("/results/")

    if request.method == "POST":

        profile = Profile.objects.get(user=user)

        Student_choices.objects.create(
            student_id=user,
            name=user.first_name + " " + user.last_name,
            gender=profile.gender,

            Q1=int(request.POST.get("q1")),
            Q2=int(request.POST.get("q2")),
            Q3=int(request.POST.get("q3")),
            Q4=int(request.POST.get("q4")),
            Q5=int(request.POST.get("q5")),
            Q6=int(request.POST.get("q6")),
            Q7=int(request.POST.get("q7")),
            Q8=int(request.POST.get("q8")),
            Q9=int(request.POST.get("q9")),
            Q10=int(request.POST.get("q10")),
        )

        return redirect("/results/")

    return render(request, "bfi_form.html")



def results_new(request):
    user = request.user

    try:
        target = Student_choices.objects.get(student_id=user)
    except Student_choices.DoesNotExist:
        return redirect("/bfi/")

    candidates = Student_choices.objects.filter(
        gender=target.gender
    ).exclude(student_id=user)

    if not candidates.exists():
        return render(request, "results.html", {"no_matches": True})

    rows = []
    ids = []

    for s in candidates:
        rows.append([
            s.extraversion, s.agreeableness, s.conscientiousness,
            s.neuroticism, s.openness
        ])
        ids.append(s.student_id.id)

    df = pd.DataFrame(rows, columns=["Ext", "Agr", "Con", "Neu", "Opn"])

    target_vec = np.array([
        target.extraversion, target.agreeableness,
        target.conscientiousness, target.neuroticism, target.openness
    ]).reshape(1, -1)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)
    target_scaled = scaler.transform(target_vec)

    profile = Profile.objects.get(user=user)

    if profile.is_premium:
        k = min(10, len(df))
    else:
        k = min(3, len(df))
        
    knn = NearestNeighbors(n_neighbors=k)
    knn.fit(X_scaled)
    distances, indices = knn.kneighbors(target_scaled)

    matches = []
    for dist, idx in zip(distances[0], indices[0]):
        match_user = Student_choices.objects.get(student_id=ids[idx])

        distance = float(dist)
        similarity = 1 / (1 + distance)  
        compatibility = round(similarity * 100, 2)


        matches.append({
            "name": match_user.name,
            "user": match_user.student_id,
            "compatibility": round(compatibility, 2),
            "distance": round(distance, 3),
            "traits": {
                "Extraversion": match_user.extraversion,
                "Agreeableness": match_user.agreeableness,
                "Conscientiousness": match_user.conscientiousness,
                "Neuroticism": match_user.neuroticism,
                "Openness": match_user.openness,
            }
        })

    return render(request, "results.html", {
        "target": target,
        "matches": matches
    })



def logout_view(request):
    logout(request)
    return redirect('/')


def profile(request):
    user = request.user

    if request.method == 'POST':
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        year = request.POST.get('year')
        gender = request.POST.get('gender')

        if not contact or not email or not year or not gender:
            messages.error(request, "All fields are required.")
            return render(request, 'profile.html')

        if Profile.objects.filter(user=user).exists():
            return redirect('/bfi/')

        if Profile.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, 'profile.html')

        if Profile.objects.filter(contact=contact).exists():
            messages.error(request, "Contact number already in use.")
            return render(request, 'profile.html')

        Profile.objects.create(
            user=user,
            contact=contact,
            email=email,
            year=year,
            gender=gender,
        )

        return redirect('/bfi/')

    return render(request, 'profile.html')


from django.shortcuts import render, redirect, get_object_or_404
from .models import profile as Profile
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def update_profile(request):
    user = request.user

    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile.contact = request.POST.get('bio', profile.contact)
        profile.gender = request.POST.get('gender', profile.gender)
        profile.year = request.POST.get('year', profile.year)
        profile.save()
        return redirect('/homepage')

    context = {
        'profile': profile
    }
    return render(request, 'update_profile.html', context)

