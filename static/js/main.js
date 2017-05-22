'use strict';

class HK {
    constructor(mainEl) {
        this.main = mainEl;

        var test = document.createElement('p')
        test.innerText = 'foo';

        this.main.appendChild(test);
        this.loadApplets();
        this.registry = {};
    }

    register(name, cls) {
        this.registry[cls.NAME] = cls;
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

    installApplet(applet) {
        var div = document.createElement('div');
        div.innerHTML = (
            '<div class="applet-title">' + applet + '</div>' +
            '<div class="applet-content">' + 'Hi!' + '</div>'
        );
        var script = document.createElement('script')
        script.onload = (event) => {
            new this.registry[applet](div);
            this.main.appendChild(div);
        };
        script.src = '/static/js/applets/' + applet + '.js';
        document.querySelector('body').appendChild(script);
    }
}
