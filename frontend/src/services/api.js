import axios from 'axios';

// Asegúrate de que este puerto coincida con tu backend (8000)
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  getStats() {
    return apiClient.get('/');
  },
  searchDrugs(query) {
    return apiClient.get(`/drugs/search?query=${query}`);
  },
  getDrugDetails(name) {
    return apiClient.get(`/drugs/${name}`);
  },
  getShortestPath(start, end) {
    return apiClient.post('/analysis/path', { start_drug: start, end_drug: end });
  },
  getAlternatives(name) {
    return apiClient.get(`/analysis/alternatives/${name}`);
  },
  filterDrugs(criteria) {
    return apiClient.post('/drugs/filter', criteria);
  }
};