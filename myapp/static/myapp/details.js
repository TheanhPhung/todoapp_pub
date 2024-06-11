document.addEventListener("DOMContentLoaded", function() {
    const missionHeader = document.querySelector(".card-header");
    const missionDetail = document.querySelector("#mission-detail");
    const editButton = document.querySelector("#edit-button");
    const cancelButton = document.querySelector("#cancel-button");

    missionDetail.style.display = "none";
    editButton.style.display = "none";
    cancelButton.style.display = "none";

    missionHeader.addEventListener("click", function() {
        if (missionDetail.style.display == "none") {
            missionDetail.style.display = "block";
            editButton.style.display = "block";
            cancelButton.style.display = "block";
        } else {
            missionDetail.style.display = "none";
            editButton.style.display = "none";
            cancelButton.style.display = "none";
        }
    })
})
