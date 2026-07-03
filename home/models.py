from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class student(models.Model):
    user=models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True)
    sleep=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    lights=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    study=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    cleanliness=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    quite=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    selfcontained=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    books=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    overnight=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    sharing=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    allergy=models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=False, blank=False)
    value=models.FloatField(default=0)

class profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    contact=models.CharField(max_length=10, validators=[MinLengthValidator(10), MaxLengthValidator(10)], unique=True)
    email=models.EmailField(unique=True)
    year=models.TextField(max_length=1)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,null=False,default='M')
    is_premium = models.BooleanField(default=False)




class Student_choices(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    student_id=models.OneToOneField(User,on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    # BFI-10 raw responses (1–5 Likert)
    Q1 = models.IntegerField()
    Q2 = models.IntegerField()
    Q3 = models.IntegerField()
    Q4 = models.IntegerField()
    Q5 = models.IntegerField()
    Q6 = models.IntegerField()
    Q7 = models.IntegerField()
    Q8 = models.IntegerField()
    Q9 = models.IntegerField()
    Q10 = models.IntegerField()

    # Computed Big Five traits
    extraversion = models.FloatField(null=True, blank=True)
    agreeableness = models.FloatField(null=True, blank=True)
    conscientiousness = models.FloatField(null=True, blank=True)
    neuroticism = models.FloatField(null=True, blank=True)
    openness = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Reverse-scored items
        r = lambda x: 6 - x

        # Compute Big Five
        self.extraversion = (self.Q1 + r(self.Q6)) / 2
        self.agreeableness = (r(self.Q2) + self.Q7) / 2
        self.conscientiousness = (self.Q3 + r(self.Q8)) / 2
        self.neuroticism = (r(self.Q4) + self.Q9) / 2
        self.openness = (self.Q5 + r(self.Q10)) / 2

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

