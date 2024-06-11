document.addEventListener("DOMContentLoaded", function() {
    console.log("Hello, World!");
})

function showDetail(mission_id) {
    const detail = document.querySelector(`#mission-${mission_id}-detail`);
    document.querySelector(`#show-${mission_id}`).onclick = function(event) {
        event.preventDefault();
        if (detail.style.display=="none") {
            detail.style.display="block";
            document.querySelector(`#show-${mission_id}`).innerText="Hide detail";
        } else {
            detail.style.display="none";
            document.querySelector(`#show-${mission_id}`).innerText="Show detail";
        }
    }
}

function showAllMissions() {
    const missions = document.querySelectorAll(".mission");
    missions.forEach(mission => {
        mission.style.display = "block";
    })
}

function showCompletedMissions() {
    const uncompleted_missions = document.querySelectorAll(".uncompleted");
    uncompleted_missions.forEach(mission => {
        mission.style.display = "none";
    })
}

function showUncompletedMissions() {
    const completed_missions = document.querySelectorAll(".completed");
    completed_missions.forEach(mission => {
        mission.style.display = "none";
    })
}
