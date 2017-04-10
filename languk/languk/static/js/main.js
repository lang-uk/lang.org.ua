window.onload = function() {
    var basicClass = document.body.getAttribute('class');
    document.body.setAttribute('class', 'loaded ' + basicClass);
};
