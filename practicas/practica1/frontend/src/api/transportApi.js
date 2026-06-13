const API_URL = "http://127.0.0.1:8000";

export async function getCities() {
    const response = await fetch(`${API_URL}/cities`);
    return response.json();
}

export async function addCity(nombre) {
    const response = await fetch(`${API_URL}/cities`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ nombre }),
    });

    return response.json();
}

export async function addConnection(data) {
    const response = await fetch(`${API_URL}/connections`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    return response.json();
}

export async function getShortestRoute(origen, destino) {
    const response = await fetch(`${API_URL}/routes/shortest`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            origen,
            destino,
        }),
    });

    return response.json();
}

export async function getAllRoutes(origen, destino) {
    const response = await fetch(`${API_URL}/routes/all`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            origen,
            destino,
        }),
    });

    return response.json();
}

export async function getConnections() {
    const response = await fetch(`${API_URL}/connections`, {
        method: "GET", 
        headers: {
            "Content-Type": "application/json",
        }
    });

    return response.json();
}
