#!/usr/bin/env python3
"""
Academic Generator Module for GI Paper Writing Tool
Uses Google Gemini API to generate academic content for each section
"""

import google.generativeai as genai
import os
from typing import Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import GEMINI_API_KEY

class AcademicGenerator:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        templates_dir = os.path.join(project_root, 'templates', 'prompts')
        
        self.prompts = {
            'abstract': self._load_prompt(os.path.join(templates_dir, 'abstract_prompt.txt')),
            'introduction': self._load_prompt(os.path.join(templates_dir, 'introduction_prompt.txt')),
            'literature_review': self._load_prompt(os.path.join(templates_dir, 'literature_prompt.txt')),
            'methodology': self._load_prompt(os.path.join(templates_dir, 'methodology_prompt.txt')),
            'results': self._load_prompt(os.path.join(templates_dir, 'results_prompt.txt')),
            'conclusion': self._load_prompt(os.path.join(templates_dir, 'conclusion_prompt.txt')),
        }

    def _load_prompt(self, path: str) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Warning: Prompt file not found: {path}")
            return "Generate academic content for this section based on the provided data: {data}"

    def generate_section(self, section: str, data: Dict[str, Any]) -> str:
        """Generate a section using Gemini and the enhanced prompt"""
        prompt = self.prompts[section].replace('{data}', self._format_data(data))
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def _format_data(self, data: Dict[str, Any]) -> str:
        # Format the data as a readable string for the prompt
        lines = []
        for k, v in data.items():
            if v:
                lines.append(f"{k.replace('_', ' ').capitalize()}: {v}")
        return '\n'.join(lines)

    def generate_full_paper(self, sections_data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Generate all sections and return a dict of section_name: content"""
        paper = {}
        for section in ['abstract', 'introduction', 'literature_review', 'methodology', 'results', 'conclusion']:
            paper[section] = self.generate_section(section, sections_data.get(section, {}))
        return paper 