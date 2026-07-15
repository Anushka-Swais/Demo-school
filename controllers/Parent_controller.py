import os
import google.generativeai as genai
from controllers.admin_controller import AdminAIController

class ParentAIController(AdminAIController):
    def __init__(self):
        super().__init__()
        
        # Dynamically load the model strictly from .env (No hardcoding!)
        model_name = os.getenv("GEMINI_MODEL")
        if not model_name:
            raise ValueError("GEMINI_MODEL is missing from environment variables.")
            
        self.model = genai.GenerativeModel(model_name)

    def generate_assessment_summary(self, student_name: str, subject: str, test_name: str, marks_obtained: float, total_marks: float, teacher_remarks: str) -> str:
        prompt = f"""
        You are an empathetic, supportive AI school counselor communicating with a parent.
        Provide a brief, clear summary of the student's performance on a recent test.
        
        Student Name: {student_name}
        Subject: {subject}
        Test Name: {test_name}
        Score: {marks_obtained}/{total_marks}
        Teacher's Notes: "{teacher_remarks}"
        
        Guidelines:
        1. Break down what this grade means simply (avoid confusing educational jargon).
        2. Keep the tone encouraging, highlighting strengths while gently addressing areas for growth.
        3. Provide 1-2 practical, easy things the parent can do at home to support their child.
        4. Keep the total response under 150 words.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def generate_due_date_alert(self, student_name: str, assignment_title: str, subject: str, due_date: str, description: str) -> str:
        prompt = f"""
        You are a helpful school assistant sending a friendly reminder alert to a parent.
        
        Student Name: {student_name}
        Assignment: {assignment_title}
        Subject: {subject}
        Due Date: {due_date}
        Task Details: {description}
        
        Create a personalized notification text. The tone should be warm, collaborative, and helpful—not stressful. 
        Briefly mention what the assignment is about and suggest how the parent can check in on their child's progress (e.g., asking to see a draft or helping gather materials).
        Keep it under 3-4 sentences.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()