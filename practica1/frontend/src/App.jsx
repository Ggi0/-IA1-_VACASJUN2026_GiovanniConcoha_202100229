import { useEffect, useState } from "react";

import "./styles/page.css";

import GraphView from "./components/GraphView";
import RouteSearch from "./components/RouteSearch";
import CityForm from "./components/CityForm";
import ConnectionForm from "./components/ConnectionForm";

import {
    getCities,
    getConnections,
    addCity,
    addConnection,
    getShortestRoute,
    getAllRoutes,
} from "./api/transportApi";


function createGraphData(
    cities,
    connections
) {
    const width = 1100;
    const height = 650;

    const centerX = width / 2;
    const centerY = height / 2;

    const radius =
        Math.min(width, height) * 0.35;

    const nodes = cities.map(
        (city, index) => {
            const angle =
                (2 *
                    Math.PI *
                    index) /
                cities.length;

            return {
                id: city,

                fx:
                    centerX +
                    radius *
                        Math.cos(
                            angle
                        ),

                fy:
                    centerY +
                    radius *
                        Math.sin(
                            angle
                        ),
            };
        }
    );

    const links =
        connections.map((c) => ({
            source: c.origen,
            target: c.destino,
            distance: c.distancia,
        }));

    return {
        nodes,
        links,
    };
}


function App() {
    const [cities, setCities] = useState([]);

    const [graphData, setGraphData] =
        useState({
            nodes: [],
            links: [],
        });

    const [result, setResult] =
        useState(null);

    const loadCities = async () => {

    try {

        const cityData =
            await getCities();

        const connectionData =
            await getConnections();

        const cities =
            cityData.ciudades || [];

        const connections =
            connectionData.connections || [];

        setCities(cities);

        setGraphData(
            createGraphData(
                cities,
                connections
            )
        );

        console.log(
            "GRAPH DATA",
            createGraphData(
                cities,
                connections
            )
        );

    } catch (error) {

        console.error(error);

    }
};

    useEffect(() => {
        loadCities();
    }, []);

    const handleAddCity = async (
        city
    ) => {
        await addCity(city);

        loadCities();
    };

    const handleAddConnection =
    async (connection) => {
        await addConnection(
            connection
        );

        await loadCities();
    };

    const shortestRoute =
        async (o, d) => {
            const data =
                await getShortestRoute(
                    o,
                    d
                );

            setResult(
                <div className="card">
                    <h4>
                        Ruta Óptima
                    </h4>

                    <p>
                        {data.ruta.join(
                            " → "
                        )}
                    </p>

                    <strong>
                        {
                            data.distancia
                        }{" "}
                        km
                    </strong>
                </div>
            );
        };

    const allRoutes = async (
        o,
        d
    ) => {
        const data =
            await getAllRoutes(o, d);

        setResult(
            <div className="card">
                <h4>
                    Todas las rutas
                </h4>

                {data.rutas.map(
                    (r, i) => (
                        <div key={i}>
                            {
                                r.ruta.join(
                                    " → "
                                )
                            }
                            {" - "}
                            {
                                r.distancia
                            }{" "}
                            km
                        </div>
                    )
                )}
            </div>
        );
    };

    return (
        <div className="page">

            <header>
                <h1>
                    Sistema de Rutas
                    Interdepartamentales
                </h1>
            </header>

            <section className="top-section">
                <GraphView
                    graphData={
                        graphData
                    }
                />

                <button
                    onClick={
                        loadCities
                    }
                >
                    Actualizar
                    Mapa
                </button>
            </section>

            <section className="middle-section">
                <CityForm
                    onAdd={
                        handleAddCity
                    }
                />

                <ConnectionForm
                    cities={
                        cities
                    }
                    onAdd={
                        handleAddConnection
                    }
                />
            </section>

            <section className="bottom-section">
                <RouteSearch
                    cities={cities}
                    onShortest={
                        shortestRoute
                    }
                    onAllRoutes={
                        allRoutes
                    }
                    result={result}
                />
            </section>

        </div>
    );
}

export default App;