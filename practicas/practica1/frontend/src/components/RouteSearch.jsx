import { useState } from "react";

export default function RouteSearch({
    cities,
    onShortest,
    onAllRoutes,
    result,
}) {
    const [origen, setOrigen] = useState("");
    const [destino, setDestino] = useState("");

    return (
        <div>
            <h3>Buscar Ruta</h3>

            <select
                value={origen}
                onChange={(e) =>
                    setOrigen(e.target.value)
                }
            >
                <option value="">
                    Origen
                </option>

                {cities.map((city) => (
                    <option key={city}>
                        {city}
                    </option>
                ))}
            </select>

            <select
                value={destino}
                onChange={(e) =>
                    setDestino(e.target.value)
                }
            >
                <option value="">
                    Destino
                </option>

                {cities.map((city) => (
                    <option key={city}>
                        {city}
                    </option>
                ))}
            </select>

            <div className="actions">
                <button
                    onClick={() =>
                        onShortest(
                            origen,
                            destino
                        )
                    }
                >
                    Ruta Más Corta
                </button>

                <button
                    onClick={() =>
                        onAllRoutes(
                            origen,
                            destino
                        )
                    }
                >
                    Todas las Rutas
                </button>
            </div>

            {result}
        </div>
    );
}