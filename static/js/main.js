'use strict';

class HK {
    constructor(mainEl) {
        this.main = mainEl;
        this.loadApplets();
        this.registry = {};
    }

    register(name, cls) {
        this.registry[name] = cls;
    }

    loadApplets() {
        fetch('/_/')
            .then((resp) => {
                return resp.json()
            })
            .then((data) => {
                Object.keys(data).forEach(key => {
                    if (key.indexOf('/') >= 0) {
                        return;
                    }

                    this.installApplet(key)
                })
            });
    }

    installApplet(appletName) {
/*        var div = document.createElement('div');
        div.innerHTML = (
            '<div class="applet-title">' + applet + '</div>' +
            '<div class="applet-content">' + 'Hi!' + '</div>'
        );
*/
        var script = document.createElement('script')
        script.onload = (event) => {
            var card = new Card(appletName);

            new this.registry[appletName](card);
            var cardDiv = document.createElement('div');
            cardDiv.appendChild(card.title);
            cardDiv.appendChild(card.content);
            this.main.appendChild(cardDiv);
        };
        script.src = '/static/js/applets/' + appletName + '.js';
        document.querySelector('body').appendChild(script);
    }
}

class Card {
    constructor(name) {
        this.title = document.createElement('div');
        this.content = document.createElement('div');

        this.title.innerText = name;
        this.title.classList.add('applet-title');
        this.content.classList.add('applet-content');
    }
}