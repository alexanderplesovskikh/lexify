"""
Author: Vlad Golub
"""

'''
This file defines Django models for a document analysis application with three main models:

1. Paragraph Model:
   - Stores document content paragraphs with reference flag
   - Fields: content text, is_reference boolean, timestamp
   - Database table: 'paragraphs'
   - Index on is_reference for faster filtering

2. UserToken Model:
   - Manages user authentication tokens and email verification
   - Fields: unique email, token string, verification code
   - Database table: 'docx_usertoken' 
   - Email field indexed for faster lookups

3. AnalysisLog Model:
   - Tracks document analysis history and results
   - Fields: user email, analysis date, file metadata, error counts
   - Stores report content and recipients as JSON
   - Database table: 'analysis_log'
   - Automatic timestamping on creation

Key features:
- Clean string representations for admin interface
- Database table names explicitly set
- Indexes on frequently queried fields
- Supports both text content and analysis metadata storage
'''

from django.db import models

class Paragraph(models.Model):
    content = models.TextField(blank=True, null=True)
    is_reference = models.BooleanField(blank=True, null=True, db_index=True)
    timestamp = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'paragraphs'
    
    def __str__(self):
        return str(self.is_reference) + " | " + str(self.content)
    
class UserToken(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'docx_usertoken'

    def __str__(self):
        return self.email
    

class AnalysisLog(models.Model):
    email = models.EmailField(db_index=True)  
    date = models.DateTimeField(auto_now_add=True)  
    file_hash = models.TextField(unique=True, blank=True, null=True)  
    error_count = models.IntegerField(default=0)  
    recipients = models.JSONField(blank=True, null=True)  
    report_text = models.TextField(blank=True, null=True)

    file_name = models.TextField(blank=True, null=True)
    file_chars = models.TextField(blank=True, null=True)
    file_time = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'analysis_log'  

    def __str__(self):
        return f"{self.email} | {self.date} | {self.file_hash}"