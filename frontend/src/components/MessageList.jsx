import { User, Calendar, CheckCircle, XCircle, Edit } from "lucide-react";
import { useState } from "react";
import AppointmentConfirmation from "./AppointmentConfirmation";

function MessageList({ messages, isLoading, messagesEndRef, onSendMessage }) {
	const [expandedConfirmation, setExpandedConfirmation] = useState(null);

	const formatTime = (date) => {
		return new Date(date).toLocaleTimeString("en-US", {
			hour: "numeric",
			minute: "2-digit",
			hour12: true,
		});
	};

	// Detect if message indicates tool/process is in progress
	const isProcessingMessage = (content) => {
		const processingPhrases = [
			"one moment",
			"let me check",
			"checking",
			"looking up",
			"searching for",
			"finding",
			"please wait",
			"give me a moment",
			"just a second",
			"working on",
			"processing",
			"hold on",
		];
		const lowerContent = content.toLowerCase();
		return processingPhrases.some((phrase) => lowerContent.includes(phrase));
	};

	// Detect if message is asking about appointment type
	const detectQuickReplies = (content) => {
		const lowerContent = content.toLowerCase();

		// Check for appointment slot listings
		// Pattern: "• Day, Month Date at Time"
		const slotPattern =
			/•\s*([A-Za-z]+,\s*[A-Za-z]+\s+\d+\s+at\s+\d+:\d+\s*(?:AM|PM))/gi;
		const slots = content.match(slotPattern);

		if (
			slots &&
			slots.length >= 2 &&
			(lowerContent.includes("available") ||
				lowerContent.includes("found") ||
				lowerContent.includes("slots") ||
				lowerContent.includes("which of these"))
		) {
			const options = slots.map((slot) => {
				// Remove the bullet point and trim
				const cleanSlot = slot.replace(/^•\s*/, "").trim();
				return {
					label: cleanSlot,
					value: `I'd like to book the ${cleanSlot} slot`,
				};
			});

			return {
				type: "time_slots",
				options: options,
			};
		}

		// Check for appointment type question
		if (
			(lowerContent.includes("purpose of your visit") ||
				lowerContent.includes("type of appointment") ||
				lowerContent.includes("kind of appointment")) &&
			(lowerContent.includes("general consultation") ||
				lowerContent.includes("follow-up") ||
				lowerContent.includes("physical exam") ||
				lowerContent.includes("specialist"))
		) {
			return {
				type: "appointment_type",
				options: [
					{
						label: "General Consultation",
						value: "I need a general consultation",
					},
					{ label: "Follow-up Visit", value: "I need a follow-up appointment" },
					{ label: "Physical Exam", value: "I need a physical exam" },
					{
						label: "Specialist Consultation",
						value: "I need a specialist consultation",
					},
				],
			};
		}

		// Check for time preference question
		if (
			(lowerContent.includes("prefer morning") ||
				(lowerContent.includes("morning") &&
					lowerContent.includes("afternoon") &&
					lowerContent.includes("evening"))) &&
			(lowerContent.includes("9 am") ||
				lowerContent.includes("12 pm") ||
				lowerContent.includes("5 pm"))
		) {
			return {
				type: "time_preference",
				options: [
					{ label: "🌅 Morning (9 AM - 12 PM)", value: "Morning, please" },
					{
						label: "☀️ Afternoon (12 PM - 5 PM)",
						value: "Afternoon would be great",
					},
					{
						label: "🌆 Evening (5 PM - 7 PM)",
						value: "Evening works best for me",
					},
				],
			};
		}

		return null;
	};

	// Function to render text with markdown formatting
	const renderFormattedText = (text) => {
		// Split by ** to find bold sections
		const parts = text.split(/(\*\*.*?\*\*)/g);

		return parts.map((part, index) => {
			// Check if this part is wrapped in **
			if (part.startsWith("**") && part.endsWith("**")) {
				const boldText = part.slice(2, -2);
				return (
					<strong
						key={index}
						className="font-semibold">
						{boldText}
					</strong>
				);
			}
			return <span key={index}>{part}</span>;
		});
	};

	// Detect if message contains appointment confirmation
	const parseAppointmentData = (content) => {
		// Look for booking confirmation patterns
		const bookingIdMatch = content.match(
			/booking[_ ]id[:\s]*([A-Z]+-\d+-\d+)/i
		);
		const confirmationCodeMatch = content.match(
			/confirmation[_ ]code[:\s]*([A-Z0-9]{6})/i
		);
		const dateMatch = content.match(
			/date[:\s]*([A-Za-z]+,\s*[A-Za-z]+\s+\d+,\s+\d{4})/i
		);

		// Check for cancellation
		const isCancelled =
			/cancel(?:led|lation)/i.test(content) && /success/i.test(content);

		// Check for reschedule
		const isRescheduled =
			/reschedule[d]?/i.test(content) && /success/i.test(content);

		if (bookingIdMatch && confirmationCodeMatch) {
			// Try to extract all appointment details from the message
			const typeMatch = content.match(
				/(?:type of )?appointment[:\s]*\*\*([^*]+)\*\*/i
			);
			const timeMatch = content.match(/time[:\s]*([0-9:]+\s*(?:AM|PM))/i);
			const patientMatch = content.match(
				/patient[_ ]name[:\s]*\*\*([^*]+)\*\*/i
			);
			const phoneMatch = content.match(/phone[_ ]number[:\s]*\*\*([^*]+)\*\*/i);
			const emailMatch = content.match(
				/email[_ ]address[:\s]*\*\*([^*]+)\*\*/i
			);
			const reasonMatch = content.match(
				/reason for visit[:\s]*\*\*([^*]+)\*\*/i
			);

			return {
				hasAppointment: true,
				type: isCancelled
					? "cancelled"
					: isRescheduled
					? "rescheduled"
					: "booked",
				booking_id: bookingIdMatch[1],
				confirmation_code: confirmationCodeMatch[1],
				appointment_type: typeMatch
					? typeMatch[1]
							.trim()
							.toLowerCase()
							.replace(" consultation", "")
							.replace("consultation", "consultation")
					: "consultation",
				date: dateMatch ? dateMatch[1] : new Date().toISOString().split("T")[0],
				start_time: timeMatch ? timeMatch[1] : "09:00",
				patient: {
					name: patientMatch ? patientMatch[1] : "Patient",
					email: emailMatch ? emailMatch[1] : "",
					phone: phoneMatch ? phoneMatch[1] : "",
				},
				reason: reasonMatch ? reasonMatch[1] : "General consultation",
				status: isCancelled ? "cancelled" : "confirmed",
			};
		}

		return { hasAppointment: false };
	};

	const formatDateForAPI = (dateStr) => {
		try {
			const date = new Date(dateStr);
			return date.toISOString().split("T")[0];
		} catch {
			return dateStr;
		}
	};

	const formatTimeForAPI = (timeStr) => {
		try {
			const match = timeStr.match(/(\d+):(\d+)\s*(AM|PM)/i);
			if (match) {
				let hours = parseInt(match[1]);
				const minutes = match[2];
				const period = match[3].toUpperCase();

				if (period === "PM" && hours !== 12) hours += 12;
				if (period === "AM" && hours === 12) hours = 0;

				return `${hours.toString().padStart(2, "0")}:${minutes}`;
			}
			return timeStr;
		} catch {
			return timeStr;
		}
	};

	return (
		<div className="flex-1 overflow-y-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-4 space-y-3 sm:space-y-4 bg-gray-50">
			{messages.map((message, index) => {
				const appointmentData =
					message.role === "assistant"
						? parseAppointmentData(message.content)
						: { hasAppointment: false };
				const showProcessing =
					message.role === "assistant" &&
					isProcessingMessage(message.content) &&
					isLoading &&
					index === messages.length - 1;
				const quickReplies =
					message.role === "assistant" &&
					index === messages.length - 1 &&
					!isLoading
						? detectQuickReplies(message.content)
						: null;

				return (
					<div key={index}>
						<div
							className={`flex items-start space-x-2 sm:space-x-3 animate-slide-in ${
								message.role === "user"
									? "flex-row-reverse space-x-reverse"
									: ""
							}`}>
							{/* Avatar */}
							<div
								className={`flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center ${
									message.role === "user"
										? "bg-primary-600"
										: message.isError
										? "bg-red-100"
										: "bg-gradient-to-br from-purple-400 to-pink-400"
								}`}>
								{message.role === "user" ? (
									<User className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
								) : (
									<span className="text-white font-semibold text-xs sm:text-sm">
										M
									</span>
								)}
							</div>

							{/* Message Content */}
							<div
								className={`flex-1 max-w-[85%] sm:max-w-[80%] lg:max-w-[75%] ${
									message.role === "user" ? "flex flex-col items-end" : ""
								}`}>
								{/* Agent Name Label */}
								{message.role === "assistant" && (
									<p className="text-xs font-medium text-gray-500 mb-1 px-2">
										Meera
									</p>
								)}
								<div
									className={`message-bubble ${
										message.role === "user"
											? "user-message"
											: message.isError
											? "bg-red-50 text-red-900 border border-red-200"
											: "agent-message"
									}`}>
									<div className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">
										{renderFormattedText(message.content)}
									</div>

									{/* Show Appointment Card Preview if confirmation detected */}
									{appointmentData.hasAppointment && (
										<div className="mt-3 pt-3 border-t border-gray-200">
											<button
												onClick={() =>
													setExpandedConfirmation(
														expandedConfirmation === index ? null : index
													)
												}
												className="w-full bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 border border-purple-200 rounded-lg p-3 transition-all flex items-center justify-between group">
												<div className="flex items-center space-x-2">
													{appointmentData.type === "cancelled" ? (
														<XCircle className="w-5 h-5 text-red-500" />
													) : appointmentData.type === "rescheduled" ? (
														<Edit className="w-5 h-5 text-purple-500" />
													) : (
														<CheckCircle className="w-5 h-5 text-green-500" />
													)}
													<span className="text-sm font-medium text-gray-900">
														{appointmentData.type === "cancelled"
															? "View Cancellation Details"
															: appointmentData.type === "rescheduled"
															? "View Rescheduled Appointment"
															: "View Appointment Confirmation"}
													</span>
												</div>
												<Calendar className="w-4 h-4 text-purple-600 group-hover:scale-110 transition-transform" />
											</button>
										</div>
									)}
								</div>

								{/* Quick Reply Buttons */}
								{quickReplies && (
									<div className="mt-3 space-y-2">
										<p className="text-xs text-gray-500 px-2">
											{quickReplies.type === "time_slots"
												? "Select a time:"
												: "Quick replies:"}
										</p>
										<div
											className={
												quickReplies.type === "time_slots"
													? "grid grid-cols-1 sm:grid-cols-2 gap-2"
													: "flex flex-wrap gap-2"
											}>
											{quickReplies.options.map((option, optionIndex) => (
												<button
													key={optionIndex}
													onClick={() =>
														onSendMessage && onSendMessage(option.value)
													}
													className={
														quickReplies.type === "time_slots"
															? "bg-white hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 border-2 border-purple-300 hover:border-purple-500 text-gray-800 hover:text-purple-700 px-4 py-3 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-sm hover:shadow-md text-sm font-medium text-left flex items-center justify-between group"
															: "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-4 py-2.5 rounded-xl transition-all duration-200 transform hover:scale-105 shadow-md hover:shadow-lg text-sm font-medium"
													}>
													<span>{option.label}</span>
													{quickReplies.type === "time_slots" && (
														<svg
															className="w-4 h-4 text-purple-400 group-hover:text-purple-600 transition-colors"
															fill="none"
															viewBox="0 0 24 24"
															stroke="currentColor">
															<path
																strokeLinecap="round"
																strokeLinejoin="round"
																strokeWidth={2}
																d="M9 5l7 7-7 7"
															/>
														</svg>
													)}
												</button>
											))}
										</div>
										{/* "None of these work" option for time slots */}
										{quickReplies.type === "time_slots" && (
											<button
												onClick={() =>
													onSendMessage &&
													onSendMessage(
														"None of these times work for me. Can you show me other dates?"
													)
												}
												className="w-full bg-gray-100 hover:bg-gray-200 border-2 border-gray-300 hover:border-gray-400 text-gray-700 px-4 py-2.5 rounded-xl transition-all duration-200 text-sm font-medium mt-2">
												📅 Show me other dates
											</button>
										)}
									</div>
								)}

								{/* Timestamp */}
								<p className="text-xs text-gray-400 mt-1 px-2">
									{formatTime(message.timestamp)}
								</p>
							</div>
						</div>

						{/* Active Processing Indicator - Shows after "let me check" type messages */}
						{showProcessing && (
							<div className="ml-10 sm:ml-12 mt-2 animate-slide-in">
								<div className="flex items-center space-x-3 bg-purple-50 border border-purple-200 rounded-xl px-4 py-3 max-w-md">
									<div className="flex space-x-1">
										<div
											className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
											style={{ animationDelay: "0ms" }}></div>
										<div
											className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
											style={{ animationDelay: "150ms" }}></div>
										<div
											className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
											style={{ animationDelay: "300ms" }}></div>
									</div>
									<span className="text-sm text-purple-700 font-medium animate-pulse">
										Working on it...
									</span>
									<svg
										className="animate-spin h-4 w-4 text-purple-600"
										xmlns="http://www.w3.org/2000/svg"
										fill="none"
										viewBox="0 0 24 24">
										<circle
											className="opacity-25"
											cx="12"
											cy="12"
											r="10"
											stroke="currentColor"
											strokeWidth="4"></circle>
										<path
											className="opacity-75"
											fill="currentColor"
											d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
									</svg>
								</div>
							</div>
						)}

						{/* Expanded Appointment Confirmation */}
						{appointmentData.hasAppointment &&
							expandedConfirmation === index && (
								<div className="mt-3 ml-10 sm:ml-12 animate-slide-up">
									<div className="bg-white rounded-xl border border-purple-200 overflow-hidden shadow-lg max-w-2xl">
										<AppointmentConfirmation
											appointment={{
												...appointmentData,
												date: formatDateForAPI(appointmentData.date),
												start_time: formatTimeForAPI(
													appointmentData.start_time
												),
												end_time: appointmentData.end_time || "10:00",
											}}
											type={appointmentData.type}
											onClose={() => setExpandedConfirmation(null)}
										/>
									</div>
								</div>
							)}
					</div>
				);
			})}

			{/* Typing Indicator */}
			{isLoading && (
				<div className="flex items-start space-x-2 sm:space-x-3 animate-slide-in">
					<div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
						<span className="text-white font-semibold text-xs sm:text-sm">
							M
						</span>
					</div>
					<div className="flex flex-col">
						<p className="text-xs font-medium text-gray-500 mb-1 px-2">Meera</p>
						<div className="message-bubble agent-message">
							<div className="typing-indicator flex space-x-1">
								<span style={{ "--delay": 0 }}></span>
								<span style={{ "--delay": 1 }}></span>
								<span style={{ "--delay": 2 }}></span>
							</div>
						</div>
					</div>
				</div>
			)}

			<div ref={messagesEndRef} />
		</div>
	);
}

export default MessageList;
