import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const sendMessage = async (message, currentEventData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      message,
      current_data: currentEventData
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const planEvent = async (eventData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/plan-event`, eventData);
    return response.data;
  } catch (error) {
    console.error('Error planning event:', error);
    throw error;
  }
};
