from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .models import *

filter_modes = [
    "Goals",
    "Projects",
    "Tasks",
    "Subtasks",
    "Uncompleted missions",
    "Completed missions",
    "All missions",
    "Overdue missions",
    "Today's Daily missions",
    "This week's Weekly missions",
    "This month's Monthly missions",
    "This year's Annual missions",
    "Missions due today",
    "Missions due this week",
    "Missions due this month",
    "Missions due this year",
]

MISSIONS = list()

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        user = request.user

        if isinstance(request.user, AnonymousUser):
            return redirect('myapp:login')

        update_failed_mission(request)
        property = Property.objects.get(owner=request.user)
        return render(request, "myapp/index.html", {
            "user": user,
            "property": property,
        })

    else:
        return redirect("myapp:login")


def register(request):
    logout(request)
    if request.method == "GET":
        return render(request, "myapp/register.html")

    else:
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if not username or not password:
            messgaes.error(request, "Register failed! Please fill out all form completely.")
            return render(request, "myapp/register.html")

        if password != confirmation:
            messages.error(request, "Register failed! Password does not match. Please try again.")
            return render(request, "myapp/register.html")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        property = Property(owner=user)
        property.save()
        messages.success(request, f"Congratulations {user.username}! Successfully registered a new account.")
        return redirect("myapp:index")


def loginView(request):
    if request.method == "GET":
        logout(request)
        return render(request, "myapp/login.html")

    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("myapp:index")

        else:
            messages.error(request, "Logged in failed! Invalid username or password. Please try again.")
            return render(request, "myapp/login.html")


def logoutView(request):
    logout(request)
    return redirect("myapp:login")


def missions(request):
    missions = Mission.objects.filter(executor=request.user, is_canceled=False, is_failed=False, is_completed=False).order_by("-id")

    if request.method == "GET":
        update_failed_mission(request)
        return render(request, "myapp/missions.html", {
            "missions": missions,
            "filter_modes": filter_modes
        })

    else:
        filter_mode = request.POST.get("filter_mode")
        missions = filter_missions(request.user, filter_mode)

        return render(request, "myapp/missions.html", {
            "missions": missions,
            "filter_modes": filter_modes
        })


def edit(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    type_choices = list(zip(*Mission.TYPE_CHOICES))[0]
    period_choices = list(zip(*Mission.PERIOD_CHOICES))[0]
    priority_choices = Mission.PRIORITY_CHOICES
    field_list = Property.objects.first().get_field_list()
    missions = Mission.objects.filter(executor=request.user, is_completed=False, is_canceled=False, is_failed=False)

    if request.method == "GET":
        deadline = mission.deadline.strftime('%Y-%m-%d') if mission.deadline else ''
        return render(request, "myapp/edit.html", {
            "mission": mission,
            "type_choices": type_choices,
            "period_choices": period_choices,
            "priority_choices": priority_choices,
            "field_list": field_list,
            "missions": missions,
            "deadline": deadline
        })

    else:
        mission.name = request.POST["name"]
        mission.describle = request.POST["describle"]
        mission.mission_type = request.POST["mission_type"]
        mission.mission_period = request.POST["mission_period"]
        mission.mission_priority = request.POST["mission_priority"]
        mission.deadline = request.POST["deadline"]

        try:
            parent_mission_id = request.POST["parent_mission"]
            mission.parent_mission = Mission.objects.get(pk=int(parent_mission_id))
        except (KeyError, ValueError):
            mission.parent_mission = None

        mission.reward_1 = request.POST["reward_1"]
        mission.reward_2 = request.POST["reward_2"]
        mission.reward_3 = request.POST["reward_3"]

        mission.save()
        parent_child_relationship(request, mission)
        if limit_by_period(request, mission) == 0:
            messages.info(request, f"Mission {mission.name} was edited!")

        return redirect("myapp:missions")


def update_models(request, mission_id):
    user = request.user
    current_level = user.level
    mission = Mission.objects.get(pk=int(mission_id))

    user.score += mission.return_score()
    user.update_level()
    user.save()
    if mission.return_score() > 0:
        messages.success(request, f"You have just received {mission.return_score():.2f} additional base points!")
    elif mission.return_score() < 0:
        messages.error(request, f"You have just lost {mission.return_score():.2f} base points!")
    else:
        messages.warning(request, f"Your base score does not change!")
    new_level = user.level

    property = Property.objects.get(owner=user)

    delta_level = new_level - current_level
    if delta_level > 0:
        for _ in range(delta_level):
            property.increment_fields()
            property.save()
        messages.success(request, f"You have just advanced {delta_level} levels and received {delta_level * 0.1:.2f} points for each attribute")

    rewards = mission.get_rewards()
    reward_score = mission.return_score() / 4.0 / 100
    for reward in rewards:
        if reward and hasattr(property, reward):
            current_value = getattr(property, reward)
            setattr(property, reward, current_value + reward_score)
            if reward_score > 0:
                messages.success(request, f"You have just received {reward_score:.2f} additional {reward} points!")
            elif reward_score < 0:
                messages.error(request, f"You have just lost {reward_score:.2f} {reward} points!")
            else:
                messages.warning(request, f"Registered properties award points unchanged")

    if mission.special_skill_reward is not None:
        skill = mission.special_skill_reward
        skill.value += reward_score
        if reward_score > 0:
            messages.success(request, f"You have just received {reward_score:.2f} additional '{skill.name}' points!")
        elif reward_score < 0:
            messages.error(request, f"You have just lost {reward_score:.2f} '{skill.name}' points!")

        skill.save()

    property.save()
    return


def finish(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    mission.is_completed = True
    mission.end_date = (timezone.now() + timedelta(hours=7)).date()
    mission.save()

    update_models(request, mission_id)

    messages.success(request, f"Mission '{mission.name}' was completed!")
    return redirect("myapp:missions")


def fail(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    mission.is_failed = True
    mission.end_date = (timezone.now() + timedelta(hours=7)).date()
    mission.save()

    update_models(request, mission_id)

    messages.error(request, f"Mission '{mission.name}' was failed!")
    return redirect("myapp:missions")


def cancel(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    mission.is_canceled = True
    mission.end_date = (timezone.now() + timedelta(hours=7)).date()
    mission.save()

    update_models(request, mission_id)

    messages.warning(request, f"Mission '{mission.name}' was canceled!")
    return redirect("myapp:missions")


def update_failed_mission(request):
    missions = Mission.objects.filter(
        executor=request.user,
        is_completed=False,
        is_failed=False,
        is_canceled=False
    )
    for mission in missions:
        if mission.auto_failed_check():
            update_models(request, mission.id)
            messages.error(request, f"Mission {mission.name} was failed!")

    return


def failure(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    if mission.base_score() <=-5:
        mission.is_failed = True
    mission.end_date = (timezone.now() + timedelta(hours=7)).date()
    mission.save()

    update_models(request, mission_id)

    messages.error(request, f"Mission '{mission.name}' was failed!")
    return redirect("myapp:missions")


def properties(request):
    update_failed_mission(request)
    property = Property.objects.get(owner=request.user)
    property.save()
    fields_dict = property.get_fields_dict()
    return render(request, "myapp/properties.html", {
        "user": request.user,
        "fields_dict": fields_dict
    })


def get_week_start_end(date):
    if isinstance(date, datetime):
        date = date.date()
    start_of_week = date - timedelta(days=date.weekday() + 1)
    if start_of_week.weekday() != 6:
        start_of_week -= timedelta(days=start_of_week.weekday() + 1)
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week, end_of_week


def get_month_start_end(date):
    if isinstance(date, datetime):
        date = date.date()
    start_of_month = date.replace(day=1)
    next_month = start_of_month.replace(month=date.month % 12 + 1, day=1)
    end_of_month = next_month - timedelta(days=1)
    return start_of_month, end_of_month


def get_year_start_end(date):
    if isinstance(date, datetime):
        date = date.date()
    start_of_year = date.replace(month=1, day=1)
    end_of_year = date.replace(month=12, day=31)
    return start_of_year, end_of_year


def filter_missions(user, filter_mode):
    missions = Mission.objects.filter(executor=user)

    if filter_mode == "Uncompleted missions":
        missions = missions.filter(is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Completed missions":
        missions = missions.filter(is_canceled=False, is_failed=False, is_completed=True)
    elif filter_mode == "All missions":
        missions = missions
    elif filter_mode == "Overdue missions":
        missions = Mission.get_overdue_missions()
        missions = missions.filter(executor=user)
    elif filter_mode == "Today's Daily missions":
        missions = missions.filter(deadline=(timezone.now() + timedelta(hours=7)).date(), mission_period="Daily")
    elif filter_mode == "This week's Weekly missions":
        start_of_week, end_of_week = get_week_start_end((timezone.now() + timedelta(hours=7)).date())
        missions = missions.filter(deadline__gte=start_of_week, deadline__lte=end_of_week, mission_period="Weekly")
    elif filter_mode == "This month's Monthly missions":
        start_of_month, end_of_month = get_month_start_end((timezone.now() + timedelta(hours=7)).date())
        missions = missions.filter(deadline__gte=start_of_month, deadline__lte=end_of_month, mission_period="Monthly")
    elif filter_mode == "This year's Annual missions":
        start_of_year, end_of_year = get_year_start_end((timezone.now() + timedelta(hours=7)).date())
        missions = missions.filter(deadline__gte=start_of_year, deadline__lte=end_of_year, mission_period="Annual")
    elif filter_mode == "Goals":
        missions = missions.filter(mission_type="Goal", is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Projects":
        missions = missions.filter(mission_type="Project", is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Tasks":
        missions = missions.filter(mission_type="Task", is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Subtasks":
        missions = missions.filter(mission_type="Subtask", is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Missions due today":
        missions = missions.filter(deadline=(timezone.now() + timedelta(hours=7)).date(), is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Missions due this week":
        start_of_week, end_of_week = get_week_start_end((timezone.now() + timedelta(hours=7)).date())
        missions = missions.filter(deadline__gte=start_of_week, deadline__lte=end_of_week, is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Missions due this month":
        start_of_month, end_of_month = get_month_start_end((timezone.now() + timedelta(hours=7)).date())
        missions = missions.filter(deadline__gte=start_of_month, deadline__lte=end_of_month, is_canceled=False, is_failed=False, is_completed=False)
    elif filter_mode == "Missions due this year":
        start_of_year, end_of_year = get_year_start_end((timezone.now() + timedelta(hours=7)).date())
        missions = missions.filter(deadline__gte=start_of_year, deadline__lte=end_of_year, is_canceled=False, is_failed=False, is_completed=False)

    return missions


def new_mission(request):
    type_choices = list(zip(*Mission.TYPE_CHOICES))[0]
    period_choices = list(zip(*Mission.PERIOD_CHOICES))[0]
    priority_choices = Mission.PRIORITY_CHOICES
    field_list = Property.objects.first().get_field_list()
    missions = Mission.objects.filter(executor=request.user, is_completed=False, is_canceled=False, is_failed=False)
    special_skills = Special_skill.objects.filter(owner=request.user)

    if request.method == "GET":
        return render(request, "myapp/new_mission.html", {
            "type_choices": type_choices,
            "period_choices": period_choices,
            "priority_choices": priority_choices,
            "field_list": field_list,
            "missions": missions,
            "special_skills": special_skills
        })

    else:
        name = request.POST["name"]
        describle = request.POST["describle"]
        mission_type = request.POST["mission_type"]
        mission_period = request.POST["mission_period"]
        mission_priority = int(request.POST["mission_priority"])
        deadline = request.POST["deadline"]

        try:
            parent_mission_id = request.POST["parent_mission"]
            parent_mission = Mission.objects.get(pk=int(parent_mission_id))
        except (KeyError, ValueError):
            parent_mission = None

        reward_1 = request.POST["reward_1"]
        reward_2 = request.POST["reward_2"]
        reward_3 = request.POST["reward_3"]

        skill_id = request.POST["special_skill_reward"]
        try:
            special_skill_reward = Special_skill.objects.get(pk=skill_id)
        except Special_skill.DoesNotExist:
            special_skill_reward = None

        mission = Mission(
            name=name,
            describle=describle,
            creator=request.user,
            executor=request.user,
            mission_type=mission_type,
            mission_period=mission_period,
            mission_priority=mission_priority,
            deadline=deadline,
            parent_mission=parent_mission,
            reward_1=reward_1,
            reward_2=reward_2,
            reward_3=reward_3,
            special_skill_reward=special_skill_reward
        )

        mission.save()
        parent_child_relationship(request, mission)
        if limit_by_period(request, mission) == 0:
            messages.info(request, f"The mission named '{mission.name}' was created successfully!")

        return render(request, "myapp/missions.html")


def details(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    milestones = Milestone.objects.filter(parent=mission, is_completed=False)
    return render(request, "myapp/details.html", {
        "mission": mission,
        "milestones": milestones
    })


def create_milestone(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    name = request.POST["name"]
    milestone = Milestone(name=name, parent=mission)
    milestone.save()
    messages.info(request, f"The milestone named '{milestone.name}' was created successfully!")
    return redirect("myapp:details", mission_id=mission.id)


def finish_milestone(request, milestone_id):
    milestone = Milestone.objects.get(pk=int(milestone_id))
    milestone.is_completed = True
    milestone.save()
    mission = milestone.parent
    messages.success(request, f"The milestone named '{milestone.name}' was completed!")
    return redirect("myapp:details", mission_id=mission.id)


def delete_milestone(request, milestone_id):
    milestone = Milestone.objects.get(pk=int(milestone_id))
    mission = milestone.parent
    milestone.delete()
    messages.warning(request, f"The milestone named '{milestone.name}' was deleted!")
    return redirect("myapp:details", mission_id=mission.id)


def mark_milestone(request, mission_id):
    mission = Mission.objects.get(pk=int(mission_id))
    mission.is_marked = True

    milestone = Milestone(name=mission.name,
                          parent=mission.parent_mission)

    mission.save()
    milestone.save()
    messages.info(request, f"Successfully marked mission named '{mission.name}' as the milestone of the mission named '{mission.parent_mission.name}'")
    return redirect("myapp:details", mission_id=mission.parent_mission.id)


def limit_by_period(request, mission):
    missions = Mission.objects.filter(executor=request.user)

    if isinstance(mission.deadline, str):
        mission.deadline = datetime.strptime(mission.deadline, "%Y-%m-%d").date()

    if mission.mission_period == "Daily":
        date_range = mission.deadline
        count = missions.filter(deadline=date_range, mission_period="Daily").count()
        if count > 1:
            messages.error(request, f"Cannot create a new Daily mission because the Daily mission limit for {mission.deadline} has been exceeded!")
            mission.delete()
            return 1

    if mission.mission_period == "Weekly":
        start_of_week, end_of_week = get_week_start_end(mission.deadline)
        count = missions.filter(deadline__gte=start_of_week, deadline__lte=end_of_week, mission_period="Weekly").count()
        if count > 3:
            messages.error(request, f"Cannot create a new Weekly mission because the Weekly mission limit from {start_of_week} to {end_of_week} has been exceeded!")
            mission.delete()
            return 1

    if mission.mission_period == "Monthly":
        start_of_month, end_of_month = get_month_start_end(mission.deadline)
        count = missions.filter(deadline__gte=start_of_month, deadline__lte=end_of_month, mission_period="Monthly").count()
        if count > 5:
            messages.error(request, f"Cannot create a new Monthly mission because the Monthly missions limit from {start_of_month} to {end_of_month} has been exceeded!")
            mission.delete()
            return 1

    if mission.mission_period == "Annual":
        start_of_year, end_of_year = get_year_start_end(mission.deadline)
        count = missions.filter(deadline__gte=start_of_year, deadline__lte=end_of_year, mission_period="Annual").count()
        if count > 10:
            messages.error(requets, f"Cannot create a new Annual mission because the Annual missions limit from {start_of_year} to {end_of_year} has been exceeded!")
            mission.delete()
            return 1

    return 0


def parent_child_relationship(request, mission):
    parent = mission.parent_mission

    if parent is None:
        return 0

    if mission.mission_type == "Goal":
        mission.parent_mission = None
        mission.save()
        messages.error(request, f"{mission.name} cannot be registered as a child of {parent.name}")
        return 1

    if mission.mission_type == "Project" and not parent.mission_type == "Goal":
        mission.parent_mission = None
        mission.save()
        messages.error(request, f"{mission.name} cannot be registered as a child of {parent.name}")
        return 1

    if mission.mission_type == "Task" and (parent.mission_type == "Task" or parent.mission_type == "Subtask"):
        mission.parent_mission = None
        mission.save()
        messages.error(request, f"{mission.name} cannot be registered as a child of {parent.name}")
        return 1

    if mission.mission_type == "Subtask":
        mission.parent_mission = None
        mission.save()
        messages.error(request, f"{mission.name} cannot be registered as a child of {parent.name}")
        return 1

    return 0


def new_special_skill(request):
    user = request.user
    special_skills = Special_skill.objects.filter(owner=user)

    if request.method == "GET":
        if user.level < 10:
            messages.warning(request, "You must reach level 10 or higher to unlock new skills.")
            return redirect("myapp:index")

        else:
            return render(request, "myapp/new_special_skill.html", {
                "special_skills": special_skills
            })

    else:
        name = request.POST["name"]

        if user.level // 10 <= special_skills.count():
            messages.warning(request, f"You must reach {(user.level + 10) - (user.level % 10)} to unlock new skill.")
            return redirect("myapp:new_special_skill")

        special_skill = Special_skill(owner=user, name=name)
        special_skill.save()

        return redirect("myapp:new_special_skill")
