document.getElementById("firstButton").addEventListener("click", () => {
    document.getElementById("add").style.display="none";
    document.getElementById("inventory").style.display="none";
    document.getElementById("products").style.display="block";
}, false);

document.getElementById("secondButton").addEventListener("click", () => {
    document.getElementById("products").style.display="none";
    document.getElementById("inventory").style.display="none";
    document.getElementById("add").style.display="block";
}, false);

document.getElementById("thirdButton").addEventListener("click", () => {
    document.getElementById("products").style.display="none";
    document.getElementById("add").style.display="none";
    document.getElementById("inventory").style.display="block";
    window.dispatchEvent(new Event("resize"));
}, false);

const { createApp } = Vue

const products = createApp({
    data() {
        return {
            message: '',
            products: []
        }
    },
    created() {
        fetch('/shopper/api/list_all/', {
            mode: 'same-origin',
            method: 'post',
            body: '',
            headers: {
                'content-type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(resp => resp.json())
        .then(json => {
            if (json.authenticated) {
                this.products = json.products,
                this.message = json.message
            } else {
                location.href = '/account/login/'
            }
        })
    },
    methods: {
        update(product) {
            fetch('/shopper/api/update_product/', {
                mode: 'same-origin',
                method: 'post',
                body: JSON.stringify({
                    'product': product
                }),
                headers: {
                    'content-type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(resp => resp.json())
            .then(json => {
                if (json.authenticated) {
                    this.message = json.message
                } else {
                    location.href = '/account/login/'
                }
            })
        }
    }
})

products.mount('#products')

const add = createApp({
    data() {
        return {
            selectedStore: {name: 'Target', shortName: 'tgt'},
            stores: [
                {name: 'Target', shortName: 'tgt'}
            ],
            message: '',
            keyword: '',
            product: {}
        }
    },
    methods: {
        clear() {
            this.selectedStore = {name: 'Target', shortName: 'tgt'},
            this.message = '',
            this.keyword = '',
            this.product = {}
        },
        search() {
            this.message = '',
            this.product = {},
            fetch('/shopper/api/search_product/', {
                mode: 'same-origin',
                method: 'post',
                body: JSON.stringify({
                    'store': this.selectedStore.shortName,
                    'keyword': this.keyword
                }),
                headers: {
                    'content-type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(resp => resp.json())
            .then(json => {
                if (json.authenticated) {
                    this.product = json.product,
                    this.message = json.message
                } else {
                    location.href = '/account/login/'
                }
            })
        },
        add() {
            fetch('/shopper/api/add_product/', {
                mode: 'same-origin',
                method: 'post',
                body: JSON.stringify({
                    'store': this.selectedStore.shortName,
                    'product': this.product
                }),
                headers: {
                    'content-type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(resp => resp.json())
            .then(json => {
                if (json.authenticated) {
                    this.message = json.message
                } else {
                    location.href = '/account/login/'
                }
            })
        }
    }
})

add.mount('#add')

const inventory = createApp({
    data() {
        return {
            message: '',
            zipcode: '',
            listView: 0,
            stores: [],
            map: null,
            geoLayer: null,
            details: []
        }
    },
    created() {
        this.getZipcode()
    },
    mounted() {
        this.initMap()
    },
    methods: {
        initMap() {
            this.map = L.map('mapContainer').setView([39.8283459,-98.5794797], 4),
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://openstreetmap.org/copyright">\
                             OpenStreetMap contributors</a>',
                maxZoom: 19
            }).addTo(this.map)
        },
        updateMap() {
            this.geoLayer = L.geoJSON({
                    'type': 'FeatureCollection',
                    'features': this.stores
                }, {
                onEachFeature: function (feature, layer) {
                    this.details = [],
                    this.details.push('<p style="text-align: center"><b>Target ' +
                        feature.properties.name + '</b><br>' +
                        feature.properties.address + '<p>'),
                    this.details.push('&emsp;&emsp;&emsp;&emsp;&emsp;<b>*****In-stock Products*****</b>'),
                    feature.properties.products.forEach(p => {
                        if (p.quantity > 0) {
                            this.details.push('<b>SKU</b>: ' + p.sku +
                                '&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;' +
                                '<b>Quantity</b>: ' + p.quantity.toString()),
                            this.details.push('<b>Name</b>: ' + p.name)
                        }
                    }),
                    layer.bindPopup(this.details.join('<br>'))
                }
            }).addTo(this.map),
            this.map.fitBounds(this.geoLayer.getBounds())
        },
        getZipcode() {
            fetch('/shopper/api/get_zipcode/', {
                mode: 'same-origin',
                method: 'post',
                body: '',
                headers: {
                    'content-type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(resp => resp.json())
            .then(json => {
                if (json.authenticated) {
                    this.zipcode = json.zipcode,
                    this.message = json.message
                } else {
                    location.href = '/account/login/'
                }
            })
        },
        list() {
            fetch('/shopper/api/list_inventory/', {
                mode: 'same-origin',
                method: 'post',
                body: JSON.stringify({
                    'zipcode': this.zipcode
                }),
                headers: {
                    'content-type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(resp => resp.json())
            .then(json => {
                if (json.authenticated) {
                    this.stores = json.stores,
                    this.message = json.message,
                    this.updateMap()
                } else {
                    location.href = '/account/login/'
                }
            })
        }
    }
})

inventory.mount('#inventory')
