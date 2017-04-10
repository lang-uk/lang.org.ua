'use strict';

window.onload = function() {

    // define Array.indexOf()
    if (!Array.prototype.indexOf) {
        Array.prototype.indexOf = function(obj, start) {
            for (var i = (start || 0), j = this.length; i < j; i++) {
                if (this[i] === obj) {
                    return i;
                }
            }
            return -1;
        }
    }



    var listArea = document.getElementById('contentsList'),
        contentsArea = document.getElementById('content'),
        headersAvailable = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'],
        resultHtml = '',
        startLevel = 0,
        lastLevel = 0,
        currentLevel = 0,
        currentNode = contentsArea.firstChild,
        anchorNode,
        headersCounter = 0,
        protector = 0,
        i;

    if (!listArea) return;



    while (currentNode != null && protector < 10000) {
        protector++;

        // process header

        currentLevel = headersAvailable.indexOf(currentNode.tagName) + 1;

        if (currentLevel) {
            headersCounter++;

            if (!startLevel) {
                startLevel = contentsArea.getElementsByTagName('H' + currentLevel).length > 1 ? currentLevel : currentLevel + 1;
                lastLevel = startLevel - 1;
            }

            if (currentLevel >= startLevel) {
                // insert anchor
                anchorNode = document.createElement('a');
                anchorNode.setAttribute('id', 'anchor' + headersCounter);
                anchorNode.setAttribute('name', 'anchor' + headersCounter);
                currentNode.parentNode.insertBefore(anchorNode, currentNode);

                // add elements to menu
                for (i = currentLevel; i < lastLevel; i++) {
                    resultHtml += '</li></ul>';
                }
                for (i = currentLevel; i > lastLevel+1; i--) {
                    resultHtml += '<ul><li>';
                }
                if (currentLevel > lastLevel) {
                    resultHtml += '<ul>';
                }
                if (currentLevel == lastLevel) {
                    resultHtml += '</li>';
                }
                resultHtml += '<li><a href="#anchor' + headersCounter + '">' + currentNode.innerHTML + '</a>';
            }

            lastLevel = currentLevel;
        }

        // look for a next node

        if (currentNode.firstChild) {
            currentNode = currentNode.firstChild;
        }
        else if (currentNode.nextSibling) {
            currentNode = currentNode.nextSibling;
        }
        else {
            while (!currentNode.nextSibling && currentNode != contentsArea) {
                currentNode = currentNode.parentNode;
            }

            if (currentNode == contentsArea) {
                // close tags in menu
                currentNode = null;
                for (i = lastLevel; i >= startLevel; i--) {
                    resultHtml += '</li></ul>';
                }
            } else {
                currentNode = currentNode.nextSibling;
            }
        }
    }

    listArea.innerHTML = resultHtml;
};
