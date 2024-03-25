const apiUrl = window.location.origin;
let emp_name = document.getElementById("emp_name")
let department = document.getElementById("department")
let photo = document.getElementById("photo")

async function postData(url = '', formData = new FormData()) {
    const response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    return await response;
}

document.getElementById("updateEncodingsBtn").onclick = async function () {
    let updateEncodingsUrl = new URL(`api/employees/encodings/`, apiUrl);
    let response = await postData(updateEncodingsUrl)
    if (response.ok) {
        alert("Encodings uploaded successfully!")
    } else {
        let errors = await response.json()
        alert(errors['errors'].join("\n"))
    }
}

document.getElementById("saveEmployeeBtn").onclick = async function () {
    let formData = new FormData();
    formData.append('photo', photo.files[0])
    formData.append('name', emp_name.value)
    formData.append('department', department.value)
    let newEmployeeUrl = new URL(`api/employees/new/`, apiUrl);
    let response = await postData(newEmployeeUrl, formData)
    if (response.ok) {
        alert("Employee data uploaded successfully!")
    } else {
        alert("Failed to save data!")
    }


}