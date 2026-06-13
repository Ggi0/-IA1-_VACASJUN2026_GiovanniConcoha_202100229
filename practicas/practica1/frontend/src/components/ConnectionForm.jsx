import { useState } from "react";

export default function ConnectionForm({
    cities,
    onAdd,
}) {
    const [origen, setOrigen] = useState("");
    const [destino, setDestino] = useState("");
    const [distancia, setDistancia] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();

        onAdd({
            origen,
            destino,
            distancia: Number(distancia),
        });

        setDistancia("");
    };

    return (
        <form onSubmit={handleSubmit}>
            <h3>Agregar Conexión</h3>

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
                    <option
                        key={city}
                        value={city}
                    >
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
                    <option
                        key={city}
                        value={city}
                    >
                        {city}
                    </option>
                ))}
            </select>

            <input
                type="number"
                placeholder="Distancia"
                value={distancia}
                onChange={(e) =>
                    setDistancia(e.target.value)
                }
            />

            <button type="submit">
                Crear
            </button>
        </form>
    );
}