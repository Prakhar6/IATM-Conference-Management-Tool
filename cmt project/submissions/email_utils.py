from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone


def send_submission_confirmation_email(submission, request=None):
    """
    Send confirmation email to authors when a submission is created
    """
    try:
        # Get all authors (primary author + co-authors)
        authors = [submission.membership.user]
        if submission.co_author1:
            authors.append(submission.co_author1)
        if submission.co_author2:
            authors.append(submission.co_author2)
        if submission.co_author3:
            authors.append(submission.co_author3)
        
        # Get current site for absolute URLs
        if request:
            current_site = get_current_site(request)
            site_domain = current_site.domain
        else:
            site_domain = 'localhost:8000'  # Fallback for development
        
        # Prepare email context
        context = {
            'submission': submission,
            'conference': submission.membership.conference,
            'authors': authors,
            'site_domain': site_domain,
            'submission_url': f"http://{site_domain}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
            'conference_url': f"http://{site_domain}{reverse('conference_detail', kwargs={'slug': submission.membership.conference.slug})}",
            'submission_date': submission.submission_date.strftime("%B %d, %Y"),
        }
        
        # Render email templates
        html_message = render_to_string('submissions/emails/submission_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Email subject
        subject = f"Submission Confirmation - {submission.paper_title}"
        
        # Send email to each author
        for author in authors:
            if author.email:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[author.email],
                    html_message=html_message,
                    fail_silently=False,
                )
        
        return True
        
    except Exception as e:
        print(f"Error sending submission confirmation email: {e}")
        return False


def send_review_notification_email(review, request=None):
    """
    Send notification email to authors when a review is submitted
    """
    try:
        submission = review.submission
        
        # Get all authors (primary author + co-authors)
        authors = [submission.membership.user]
        if submission.co_author1:
            authors.append(submission.co_author1)
        if submission.co_author2:
            authors.append(submission.co_author2)
        if submission.co_author3:
            authors.append(submission.co_author3)
        
        # Get current site for absolute URLs
        if request:
            current_site = get_current_site(request)
            site_domain = current_site.domain
        else:
            site_domain = 'localhost:8000'  # Fallback for development
        
        # Prepare email context
        context = {
            'review': review,
            'submission': submission,
            'conference': submission.membership.conference,
            'reviewer': review.reviewer,
            'authors': authors,
            'site_domain': site_domain,
            'submission_url': f"http://{site_domain}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
            'conference_url': f"http://{site_domain}{reverse('conference_detail', kwargs={'slug': submission.membership.conference.slug})}",
            'review_date': review.date_reviewed.strftime("%B %d, %Y") if review.date_reviewed else timezone.now().strftime("%B %d, %Y"),
        }
        
        # Render email templates
        html_message = render_to_string('submissions/emails/review_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Email subject
        recommendation_text = review.get_recommendation_display() if hasattr(review, 'get_recommendation_display') else review.recommendation
        subject = f"Review Received - {submission.paper_title} ({recommendation_text})"
        
        # Send email to each author
        for author in authors:
            if author.email:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[author.email],
                    html_message=html_message,
                    fail_silently=False,
                )
        
        return True
        
    except Exception as e:
        print(f"Error sending review notification email: {e}")
        return False


def send_reviewer_assignment_email(review, request=None):
    """
    Send notification email to reviewer when assigned to review a submission
    """
    try:
        submission = review.submission
        
        # Get current site for absolute URLs
        if request:
            current_site = get_current_site(request)
            site_domain = current_site.domain
        else:
            site_domain = 'localhost:8000'  # Fallback for development
        
        # Prepare email context
        context = {
            'review': review,
            'submission': submission,
            'conference': submission.membership.conference,
            'reviewer': review.reviewer,
            'site_domain': site_domain,
            'review_url': f"http://{site_domain}{reverse('submit_review', kwargs={'review_id': review.pk})}",
            'submission_url': f"http://{site_domain}{reverse('submission_detail', kwargs={'pk': submission.pk})}",
            'assignment_date': review.date_assigned.strftime("%B %d, %Y") if review.date_assigned else timezone.now().strftime("%B %d, %Y"),
        }
        
        # Render email templates
        html_message = render_to_string('submissions/emails/reviewer_assignment.html', context)
        plain_message = strip_tags(html_message)
        
        # Email subject
        subject = f"Review Assignment - {submission.paper_title}"
        
        # Send email to reviewer
        if review.reviewer.email:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[review.reviewer.email],
                html_message=html_message,
                fail_silently=False,
            )
        
        return True
        
    except Exception as e:
        print(f"Error sending reviewer assignment email: {e}")
        return False
