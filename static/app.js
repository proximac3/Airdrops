
// send post request to local host.
async function sendProjectId(id, project_name,action) {
    const response = await axios.post(`http://127.0.0.1:5000//bitdrops/favorites/${action}`,
        {
            id: `${id}`,
            projectName: `${project_name}`
        }
    );
    return response.data
};


// ADD AND REMOVE project form favorites
$('.favorite_icon').click(function (e) {
    if (e.target.className.includes('favorite_icon_selected')) {
        // if element's in favorites removes from favorites
        sendProjectId(e.target.id, e.target.dataset.pn, 'remove')
        e.target.classList.remove('favorite_icon_selected')
    
    } else if (e.target.className.includes('favorite_icon_selected') == false) {
        // if element not in favorites add to favorites
        e.target.classList.add('favorite_icon_selected')
        sendProjectId(e.target.id, e.target.dataset.pn, 'add')
    }
});


// Favorite reminder pop up menu
const $popupMenu = $('.popup')[0]
// project card
const $projectCard = $('.project-card')
// flah message
const $flash = $('.flash')[0]

// project data
 let projectID, projectName, startDate, endDate,userEmail

// project reminder bell icon
$('.reminder').click(function (e) {
    // display pop up menu
    $popupMenu.style.display = ''
    
    // blur background
    for (const element of $projectCard) {
        element.style.filter = 'blur(5px)'
    };
    
    $('.reminder-project').text(`Project : ${e.target.dataset.pn}`)

    projectID = e.target.id
    projectName = e.target.dataset.pn
});

// Close pop up menu
$('.cancel-button').click(function () {
    $popupMenu.style.display = 'none'
    for (const element of $projectCard) {
        element.style.filter = 'blur(0px)'
    };
})


// send reminder form
$('.reminder-submit').click(async function (e) {
    e.preventDefault()
    // get data from form
    const $formValue = $('#reminder').val()
    console.log($formValue)
    // close pop up 
    $popupMenu.style.display = 'none'

    // remove blur from background
    for (const element of $projectCard) {
        element.style.filter = 'blur(0px)'
    };

    // send data to server
    const response = await axios.post(`http://127.0.0.1:5000//bitdrops/reminder`,
        {
            id: `${projectID}`,
            projectName: `${projectName}`,
            value: `${$formValue}`
        }
    );
    
    // display flash messages
    $flash.innerText = response.data.message
});


















