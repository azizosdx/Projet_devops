import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const ReservationForm = () => {
  const navigate = useNavigate();
  const [salles, setSalles] = useState([]);
  const [formData, setFormData] = useState({
    salle_id: '',
    start_time: '',
    end_time: '',
    description: ''
  });
  const [error, setError] = useState('');

  // Récupérer la liste des salles disponibles
  useEffect(() => {
    const fetchSalles = async () => {
      try {
        const response = await axios.get('http://localhost:5002/salles');
        setSalles(response.data.filter(salle => salle.available));
      } catch (err) {
        setError('Erreur lors du chargement des salles');
      }
    };
    fetchSalles();
  }, []);

  // Gestion de la soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    if (!token) {
      navigate('/login');
      return;
    }

    try {
      await axios.post('http://localhost:5003/reserve', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      alert('Réservation envoyée avec succès !');
      navigate('/salles');
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors de la réservation');
    }
  };

  // Mise à jour des champs du formulaire
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Réserver une Salle</h1>
        
        {error && (
          <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Salle</label>
            <select
              name="salle_id"
              value={formData.salle_id}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
              required
            >
              <option value="">Sélectionnez une salle</option>
              {salles.map(salle => (
                <option key={salle.id} value={salle.id}>
                  {salle.name} (Capacité : {salle.capacity})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Date et Heure de Début</label>
            <input
              type="datetime-local"
              name="start_time"
              value={formData.start_time}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Date et Heure de Fin</label>
            <input
              type="datetime-local"
              name="end_time"
              value={formData.end_time}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Description (Optionnel)</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
              rows={3}
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition"
          >
            Réserver
          </button>
        </form>
      </div>
    </div>
  );
};

export default ReservationForm;