from datetime import datetime
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils import timezone

# Create your models here.
def fibonaci_sequence(level):
    if level == 0 or level == 1:
        return 10
    else:
        return fibonaci_sequence(level - 2) + fibonaci_sequence(level - 1)


class User(AbstractUser):
    SEX_CHOICES = [
        ("Unknown", "Unknown"),
        ("Male", "Male"),
        ("Female", "Female")
    ]

    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default="Unknown")
    date_of_birth = models.DateField(null=True, blank=True)
    level = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)

    def age(self):
        if not self.date_of_birth:
            return 30
        else:
            year_delta = timezone.now().year - self.date_of_birth.year
            if timezone.now().month > self.date_of_birth.year:
                year_delta -= 1
            return year_delta


    def level_score(self):
        return fibonaci_sequence(self.level)

    def update_level(self):
        while True:
            if self.score < fibonaci_sequence(self.level):
                break
            self.score -= fibonaci_sequence(self.level)
            self.level += 1

class Mission(models.Model):
    TYPE_CHOICES = [
        ("Goal", "Goal"),
        ("Project", "Project"),
        ("Task", "Task"),
        ("Subtask", "Subtask")
    ]

    PERIOD_CHOICES = [
        ("Daily", "Daily"),
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
        ("Annual", "Annual"),
        ("Normal", "Normal"),
        ("Angel", "Angel"),
        ("Penalty", "Penalty")
    ]

    PRIORITY_CHOICES = [
        (1, "Not urgent and not important"),
        (2, "Urgent but not important"),
        (3, "Not urgent but important"),
        (4, "Urgent and important")
    ]

    name = models.CharField(max_length=200)
    describle = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, max_length=20, on_delete=models.CASCADE)
    executor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="missions")
    mission_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="Task")
    mission_period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="Normal")
    mission_priority = models.IntegerField(choices=PRIORITY_CHOICES, default=0)
    parent_mission = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    innitiated_date = models.DateField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    reward_1 = models.CharField(max_length=30, null=True, blank=True)
    reward_2 = models.CharField(max_length=30, null=True, blank=True)
    reward_3 = models.CharField(max_length=30, null=True, blank=True)
    is_marked = models.BooleanField(default=False)
    special_skill_reward = models.ForeignKey("Special_skill", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_rewards(self):
        return [self.reward_1, self.reward_2, self.reward_3]

    def is_overdue(self):
        return timezone.now() > self.deadline

    @classmethod
    def get_overdue_missions(cls):
        return cls.objects.filter(deadline__lt=timezone.now(), is_completed=False, is_failed=False, is_canceled=False)

    def auto_failed_check(self):
        if datetime.now().date() >= self.deadline + timedelta(days=4):
            self.is_failed = True
            self.end_date = (timezone.now() + timedelta(hours=7)).date()
            self.save()
            return True
        return False

    def base_score(self):
        if not self.deadline or not self.end_date or self.is_canceled:
            return 0
        if self.is_failed:
            return -5
        timedelta = self.deadline - self.end_date
        if timedelta.days >= 0:
            return timedelta.days + 1
        else:
            return timedelta.days - 1

    def k_mission_type(self):
        if self.mission_type == "Goal":
            return 10.0
        elif self.mission_type == "Project":
            return 5.0
        elif self.mission_type == "Task":
            return 1.0
        else:
            return 0.5

    def k_mission_period(self):
        if self.mission_period == "Daily":
            return 2
        elif self.mission_period == "Weekly":
            return 3
        elif self.mission_period == "Monthly":
            return 5
        elif self.mission_period == "Annual":
            return 10
        elif self.mission_period == "Normal":
            return 1
        elif self.mission_period == "Angel":
            if self.base_score() > 0:
                return 1
            else:
                return 0
        else:
            if self.base_score() > 0:
                return 0
            else:
                return 1

    def k_mission_priority(self):
        return self.mission_priority

    def return_score(self):
        return self.base_score() * self.k_mission_type() * self.k_mission_period() * self.k_mission_priority()

    def progress(self):
        milestones = Milestone.objects.filter(parent=self)
        if milestones.count() == 0:
            return 0
        milestones_completed = milestones.filter(is_completed=True)
        return float(milestones_completed.count() * 100/ milestones.count())


class Milestone(models.Model):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="milestones")
    is_completed = models.BooleanField(default=False)
    is_deleted= models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Property(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    confident = models.FloatField(default=10.0)
    decisive= models.FloatField(default=10.0)
    discipline = models.FloatField(default=10.0)
    difficulty_overcoming = models.FloatField(default=10.0)
    resourceful = models.FloatField(default=10.0)

    def mentality(self):
        fields = [
            self.confident,
            self.decisive,
            self.discipline,
            self.difficulty_overcoming,
            self.resourceful
        ]
        return sum(fields) / len(fields)

    smart = models.FloatField(default=10.0)
    memorize = models.FloatField(default=10.0)
    deductive = models.FloatField(default=10.0)
    reaction = models.FloatField(default=10.0)
    general_knowledge = models.FloatField(default=10.0)
    planning = models.FloatField(default=10.0)

    def brain(self):
        fields = [
            self.smart,
            self.memorize,
            self.deductive,
            self.reaction,
            self.general_knowledge,
            self.planning
        ]
        return sum(fields) / len(fields)

    power = models.FloatField(default=10.0)
    endurance = models.FloatField(default=10.0)
    agile = models.FloatField(default=10.0)
    resistance = models.FloatField(default=10.0)
    skillful = models.FloatField(default=10.0)
    good_looking = models.FloatField(default=10.0)

    def physical(self):
        fields = [
            self.power,
            self.endurance,
            self.agile,
            self.resistance,
            self.skillful,
            self.good_looking
        ]
        return sum(fields) / len(fields)

    income = models.FloatField(default=10.0)
    asset = models.FloatField(default=10.0)
    financial_management = models.FloatField(default=10.0)

    def financial(self):
        fields = [
            self.income,
            self.asset,
            self.financial_management
        ]
        return sum(fields) / len(fields)

    conversation = models.FloatField(default=10.0)
    friendly = models.FloatField(default=10.0)
    connection = models.FloatField(default=10.0)

    def social_skill(self):
        fields = [
            self.conversation,
            self.friendly,
            self.connection
        ]
        return sum(fields) / len(fields)

    def __str__(self):
        return f"{self.owner.username}'s properties;"

    def get_field_list(self):
        return [field.name for field in self._meta.get_fields() if isinstance(field, models.FloatField)]

    def get_fields_dict(self):
        fields_dict = {field.name: getattr(self, field.name) for field in self._meta.get_fields() if isinstance(field, models.FloatField)}
        return fields_dict

    def increment_fields(self):
        for field in self._meta.get_fields():
            if isinstance(field, models.FloatField):
                current_value = getattr(self, field.name)
                setattr(self, field.name, current_value + 0.1)
        self.save()

    def average_all_fields(self):
        float_fields = [getattr(self, field.name) for field in self._meta.get_fields() if isinstance(field, models.FloatField)]
        return sum(float_fields) / len(float_fields)


class Special_skill(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.FloatField(default=10.0)
    registration_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
