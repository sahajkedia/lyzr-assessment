import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ChatAPI {
	constructor() {
		this.client = axios.create({
			baseURL: API_BASE_URL,
			headers: {
				"Content-Type": "application/json",
			},
		});
	}

	async sendMessage(message, conversationHistory = [], sessionId = null) {
		try {
			const response = await this.client.post("/api/chat", {
				message,
				conversation_history: conversationHistory,
				session_id: sessionId,
			});
			return response.data;
		} catch (error) {
			console.error("Error sending message:", error);
			throw new Error(
				error.response?.data?.detail ||
					"Failed to send message. Please try again."
			);
		}
	}

	async checkHealth() {
		try {
			const response = await this.client.get("/health");
			return response.data;
		} catch (error) {
			console.error("Health check failed:", error);
			return { status: "unhealthy" };
		}
	}

	async clearSession(sessionId) {
		try {
			await this.client.delete(`/api/chat/${sessionId}`);
			return true;
		} catch (error) {
			console.error("Error clearing session:", error);
			return false;
		}
	}

	// Calendly API methods
	async getAppointmentByConfirmation(confirmationCode) {
		try {
			const response = await this.client.get(
				`/api/calendly/appointment/confirmation/${confirmationCode}`
			);
			return response.data;
		} catch (error) {
			console.error("Error fetching appointment:", error);
			throw new Error(
				error.response?.data?.detail || "Failed to fetch appointment details."
			);
		}
	}

	async getAppointmentById(bookingId) {
		try {
			const response = await this.client.get(
				`/api/calendly/appointment/${bookingId}`
			);
			return response.data;
		} catch (error) {
			console.error("Error fetching appointment:", error);
			throw new Error(
				error.response?.data?.detail || "Failed to fetch appointment details."
			);
		}
	}

	async cancelAppointment(bookingId, reason = null) {
		try {
			const params = reason ? { reason } : {};
			const response = await this.client.delete(
				`/api/calendly/cancel/${bookingId}`,
				{ params }
			);
			return response.data;
		} catch (error) {
			console.error("Error canceling appointment:", error);
			throw new Error(
				error.response?.data?.detail || "Failed to cancel appointment."
			);
		}
	}

	async deleteAppointment(bookingId, permanent = false) {
		try {
			const response = await this.client.delete(
				`/api/appointments/${bookingId}`,
				{
					params: { permanent },
				}
			);
			return response.data;
		} catch (error) {
			console.error("Error deleting appointment:", error);
			throw new Error(
				error.response?.data?.detail || "Failed to delete appointment."
			);
		}
	}

	async rescheduleAppointment(bookingId, newDate, newTime) {
		try {
			const response = await this.client.post(
				`/api/calendly/reschedule/${bookingId}`,
				null,
				{
					params: {
						new_date: newDate,
						new_time: newTime,
					},
				}
			);
			return response.data;
		} catch (error) {
			console.error("Error rescheduling appointment:", error);
			throw new Error(
				error.response?.data?.detail || "Failed to reschedule appointment."
			);
		}
	}

	async checkAvailability(date, appointmentType) {
		try {
			const response = await this.client.get("/api/calendly/availability", {
				params: {
					date,
					appointment_type: appointmentType,
				},
			});
			return response.data;
		} catch (error) {
			console.error("Error checking availability:", error);
			throw new Error(
				error.response?.data?.detail || "Failed to check availability."
			);
		}
	}

	async getNextAvailableDates(appointmentType, days = 7) {
		try {
			const response = await this.client.get(
				"/api/calendly/availability/next-dates",
				{
					params: {
						appointment_type: appointmentType,
						days,
					},
				}
			);
			return response.data;
		} catch (error) {
			console.error("Error fetching next available dates:", error);
			throw new Error(
				error.response?.data?.detail || "Failed to fetch available dates."
			);
		}
	}
}

export const chatAPI = new ChatAPI();
