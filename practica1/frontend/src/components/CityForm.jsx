import { useState } from "react";

export default function CityForm({ onAdd }) {
    const [city, setCity] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!city.trim()) return;

        onAdd(city);

        setCity("");
    };

    return (
        <form onSubmit={handleSubmit}>
            <h3>Agregar Ciudad</h3>

            <input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="Nombre ciudad"
            />

            <button type="submit">
                Agregar
            </button>
        </form>
    );
}