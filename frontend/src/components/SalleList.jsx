import React, { useEffect, useState } from 'react';

const SalleList = () => {
  const [salles, setSalles] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5002/salles')
      .then(res => res.json())
      .then(data => setSalles(data));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Liste des Salles</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {salles.map(salle => (
          <div key={salle.id} className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold">{salle.name}</h2>
            <p>Capacité : {salle.capacity}</p>
            <p className={salle.available ? 'text-green-500' : 'text-red-500'}>
              {salle.available ? 'Disponible' : 'Occupée'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SalleList;