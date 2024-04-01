document.addEventListener("DOMContentLoaded", function () {
    let modal = document.getElementById("myModal");


    const photos = document.querySelectorAll(".photo")
    let modalImg = document.getElementById("img01");
    let captionText = document.getElementById("caption");
    photos.forEach(function (c) {
                        // ��� ������ ����������
                        c.onclick = function () {
                            // ������� �������
                            // ���� ������, �� �������� ��� option, ������� � ������ ������.
                            modal.style.display = "block";
                            modalImg.src = c.src;
                            captionText.innerHTML = c.alt;
                        };
                     })

    let span = document.getElementsByClassName("close")[0];

    span.onclick = function() {
      modal.style.display = "none";
    }
})