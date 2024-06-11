document.addEventListener("DOMContentLoaded", function() {
    console.log("Hello, World!");

    const details = document.querySelectorAll('.details');
    details.forEach(detail => {
        detail.style.display = 'none';
        let mission_id = detail.id.split('-')[1];
        addHoverListeners(mission_id);
    });

    document.querySelector("#mission-filter").addEventListener("change", function() {
        document.querySelector("#filter-form").submit();
    });
});

function addHoverListeners(mission_id) {
    const missionElement = document.querySelector(`#mission-${mission_id}`);
    const detailElement = document.querySelector(`#mission-${mission_id}-detail`);

    missionElement.addEventListener('mouseover', function() {
        detailElement.style.display = 'block';
    });

    missionElement.addEventListener('mouseout', function() {
        detailElement.style.display = 'none';
    });
}
