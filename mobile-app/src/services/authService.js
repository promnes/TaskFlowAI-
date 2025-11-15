import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_ENDPOINTS } from '../constants/config';

class AuthService {
  async login(phoneNumber) {
    try {
      const response = await api.post(API_ENDPOINTS.LOGIN, {
        phone_number: phoneNumber,
      });
      
      const { access_token, user_id, customer_code } = response.data;
      
      // Store token
      await AsyncStorage.setItem('authToken', access_token);
      await AsyncStorage.setItem('userId', user_id.toString());
      await AsyncStorage.setItem('customerCode', customer_code || '');
      
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Login failed';
    }
  }

  async register(userData) {
    try {
      const response = await api.post(API_ENDPOINTS.REGISTER, userData);
      
      const { access_token, user_id, customer_code } = response.data;
      
      // Store token
      await AsyncStorage.setItem('authToken', access_token);
      await AsyncStorage.setItem('userId', user_id.toString());
      await AsyncStorage.setItem('customerCode', customer_code || '');
      
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Registration failed';
    }
  }

  async logout() {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('userId');
    await AsyncStorage.removeItem('customerCode');
  }

  async isAuthenticated() {
    const token = await AsyncStorage.getItem('authToken');
    return !!token;
  }

  async getToken() {
    return await AsyncStorage.getItem('authToken');
  }

  async getCurrentUser() {
    try {
      const response = await api.get(API_ENDPOINTS.PROFILE);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Failed to fetch user';
    }
  }
}

export default new AuthService();
