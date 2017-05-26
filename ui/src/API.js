class API {
    constructor(url) {
        if (!url.endsWith('/')) {
            url += '/';
        }

        this.url = url;
    }

    get(path) {
        if (path.startsWith('/')) {
            path = path.slice(1);
        }
        if (path.endsWith('/')) {
            path = path.slice(0, -1);
        }
        return new Promise((resolve, reject) => {
            fetch(this.url + path)
            .then((resp) => {
                return resp.json()}
            )
            .then((data) =>
                resolve(data.result)
            )
            .catch((e) => {
                console.log('Error:', e)
            });
        });
    }

    post(path, data) {
        if (path.startsWith('/')) {
            path = path.slice(1);
        }
        if (path.endsWith('/')) {
            path = path.slice(0, -1);
        }
        data = data || {};

        return new Promise((resolve, reject) => {
            fetch(this.url + path, {
              method: 'POST',
              body: JSON.stringify(data),
              headers: new Headers({
                'Content-Type': 'application/json'
              })
            })
            .then((resp) => {
                return resp.json()}
            )
            .then((data) =>
                resolve(data.result)
            )
            .catch((e) => {
                console.log('Error:', e)
            });
        });
    }
}

export default API;
