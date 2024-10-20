
function toggleDescription(element) {
    const description = element.previousElementSibling;
    const fullDescription = element.nextElementSibling;

    if (description.style.display === 'none') {
        description.style.display = '-webkit-box';
        fullDescription.style.display = 'none';
        element.textContent = '... more';
    } else {
        description.style.display = 'none';
        fullDescription.style.display = 'block';
        element.textContent = '... less';
    }
}
