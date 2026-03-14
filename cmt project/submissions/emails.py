from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_submission_confirmation(submission, request=None):
    """Send confirmation email to author and co-authors after paper submission."""
    conference = submission.membership.conference
    author = submission.membership.user

    # Build author list
    authors = [author]
    for co_author in [submission.co_author1, submission.co_author2, submission.co_author3]:
        if co_author:
            authors.append(co_author)

    # Build URLs
    base_url = request.build_absolute_uri('/') if request else ''
    submission_url = f"{base_url}submissions/{submission.pk}/"
    conference_url = f"{base_url}conference/{conference.slug}/"

    context = {
        'conference': conference,
        'submission': submission,
        'authors': authors,
        'submission_date': timezone.now().strftime('%B %d, %Y'),
        'submission_url': submission_url,
        'conference_url': conference_url,
    }

    html_message = render_to_string('submissions/emails/submission_confirmation.html', context)

    # Send to all authors
    recipients = [a.email for a in authors]
    try:
        send_mail(
            subject=f"Submission Confirmation: {submission.paper_title}",
            message=f"Your paper '{submission.paper_title}' has been submitted to {conference.conference_name}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
        )
    except Exception as e:
        logger.error(f"Failed to send submission confirmation email: {e}")


def send_reviewer_assignment(review, request=None):
    """Send notification to reviewer when assigned to a paper."""
    submission = review.submission
    conference = submission.membership.conference
    reviewer = review.reviewer

    base_url = request.build_absolute_uri('/') if request else ''
    review_url = f"{base_url}review/submit/{review.pk}/"
    submission_url = f"{base_url}submissions/{submission.pk}/"
    conference_url = f"{base_url}conference/{conference.slug}/"

    context = {
        'conference': conference,
        'submission': submission,
        'reviewer': reviewer,
        'assignment_date': timezone.now().strftime('%B %d, %Y'),
        'review_url': review_url,
        'submission_url': submission_url,
        'conference_url': conference_url,
    }

    html_message = render_to_string('submissions/emails/reviewer_assignment.html', context)

    try:
        send_mail(
            subject=f"Review Assignment: {submission.paper_title}",
            message=f"You have been assigned to review '{submission.paper_title}' for {conference.conference_name}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reviewer.email],
            html_message=html_message,
        )
    except Exception as e:
        logger.error(f"Failed to send reviewer assignment email: {e}")


def send_review_notification(review, request=None):
    """Send notification to author when a review is submitted."""
    submission = review.submission
    conference = submission.membership.conference
    author = submission.membership.user
    reviewer = review.reviewer

    base_url = request.build_absolute_uri('/') if request else ''
    submission_url = f"{base_url}submissions/{submission.pk}/"
    conference_url = f"{base_url}conference/{conference.slug}/"

    context = {
        'conference': conference,
        'submission': submission,
        'review': review,
        'reviewer': reviewer,
        'review_date': timezone.now().strftime('%B %d, %Y'),
        'submission_url': submission_url,
        'conference_url': conference_url,
    }

    html_message = render_to_string('submissions/emails/review_notification.html', context)

    # Send to author and co-authors
    recipients = [author.email]
    for co_author in [submission.co_author1, submission.co_author2, submission.co_author3]:
        if co_author:
            recipients.append(co_author.email)

    try:
        send_mail(
            subject=f"Review Received: {submission.paper_title}",
            message=f"A review has been submitted for your paper '{submission.paper_title}'.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
        )
    except Exception as e:
        logger.error(f"Failed to send review notification email: {e}")


def send_registration_confirmation(user, conference, membership):
    """Send confirmation email after conference registration + payment."""
    try:
        send_mail(
            subject=f"Registration Confirmed: {conference.conference_name}",
            message=(
                f"Dear {user.get_full_name()},\n\n"
                f"Your registration for {conference.conference_name} has been confirmed.\n"
                f"Role: {membership.role1}"
                f"{', ' + membership.role2 if membership.role2 != 'N/A' else ''}\n\n"
                f"Thank you for registering!\n\n"
                f"IATM Conference Management System"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
    except Exception as e:
        logger.error(f"Failed to send registration confirmation email: {e}")
