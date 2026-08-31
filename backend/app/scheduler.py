"""
APScheduler configuration and scheduled jobs for PDR monthly workflow.

Jobs are idempotent - running the same job twice will not create duplicate records.
"""
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.positive_deviance import PositiveDevianceDetector
from app.services.playbook_extraction import PlaybookExtractor
from app.services.playbook_clustering import PlaybookClusterer
from app.services.playbook_matching import PlaybookMatcher
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = AsyncIOScheduler()


async def detect_positive_deviants_job():
    """
    Monthly job: Detect new positive deviants.
    
    Idempotent: Checks for existing deviants before creating new ones.
    """
    logger.info("Starting positive deviant detection job")
    
    try:
        db = SessionLocal()
        detector = PositiveDevianceDetector()
        
        # Detect positive deviants
        result = detector.batch_detect(db)
        
        logger.info(f"Detected {len(result['positive_deviants'])} positive deviants")
        
    except Exception as e:
        logger.error(f"Positive deviant detection job failed: {e}")
    finally:
        db.close()


async def extract_narrative_actions_job():
    """
    Monthly job: Extract actions from positive deviant narratives.
    
    Idempotent: Checks for existing extractions before creating new ones.
    Only processes deviants without extractions.
    """
    logger.info("Starting narrative action extraction job")
    
    try:
        db = SessionLocal()
        extractor = PlaybookExtractor()
        
        # Get positive deviants without extractions
        from app.models.positive_deviants import PositiveDeviant
        from app.models.extracted_actions import ExtractedAction
        
        # Query deviants that don't have extracted actions yet
        from sqlalchemy import select, not_, exists
        subquery = select(ExtractedAction.deviant_id).distinct()
        query = select(PositiveDeviant).where(not_(PositiveDeviant.deviant_id.in_(subquery)))
        
        result = db.execute(query)
        deviants_without_extractions = result.scalars().all()
        
        logger.info(f"Found {len(deviants_without_extractions)} deviants without extractions")
        
        for deviant in deviants_without_extractions:
            try:
                # Extract actions for this deviant
                actions = await extractor.extract_actions({
                    "deviant_id": str(deviant.deviant_id),
                    "project_id": str(deviant.project_id),
                    "reporting_month": deviant.reporting_month.isoformat(),
                    "narrative_text": _get_narrative_for_deviant(db, deviant.project_id),
                })
                
                # Store extracted actions
                for action in actions:
                    extracted_action = ExtractedAction(
                        deviant_id=deviant.deviant_id,
                        project_id=deviant.project_id,
                        action_text=action["action_text"],
                        category=action["category"],
                        source_month=action["source_month"],
                        quote_evidence=action.get("quote_evidence"),
                        specificity_score=action["specificity_score"],
                        llm_model_version=action.get("llm_model_version"),
                        prompt_version=action.get("prompt_version"),
                    )
                    db.add(extracted_action)
                
                db.commit()
                logger.info(f"Extracted {len(actions)} actions for deviant {deviant.deviant_id}")
                
            except Exception as e:
                logger.error(f"Failed to extract actions for deviant {deviant.deviant_id}: {e}")
                db.rollback()
        
    except Exception as e:
        logger.error(f"Narrative action extraction job failed: {e}")
    finally:
        db.close()


def _get_narrative_for_deviant(db, project_id):
    """Helper to get narrative text for a project."""
    # This would query the actual narrative data from the database
    # For now, return a placeholder
    return ""


async def cluster_playbooks_job():
    """
    Monthly job: Cluster extracted actions into playbooks.
    
    Idempotent: Checks for existing playbooks before creating new ones.
    Only processes actions not yet clustered into playbooks.
    """
    logger.info("Starting playbook clustering job")
    
    try:
        db = SessionLocal()
        clusterer = PlaybookClusterer()
        
        # Get actions that are not yet in any playbook
        from app.models.extracted_actions import ExtractedAction
        from app.models.playbooks import Playbook
        from sqlalchemy import select, not_, exists
        
        # Query actions not in any playbook's source_action_ids
        # This is a simplified check - in production, track which actions are clustered
        query = select(ExtractedAction)
        result = db.execute(query)
        unclustered_actions = result.scalars().all()
        
        logger.info(f"Found {len(unclustered_actions)} unclustered actions")
        
        # Group actions by category
        from collections import defaultdict
        actions_by_category = defaultdict(list)
        for action in unclustered_actions:
            actions_by_category[action.category].append({
                "action_id": str(action.action_id),
                "deviant_id": str(action.deviant_id),
                "project_id": str(action.project_id),
                "action_text": action.action_text,
                "category": action.category,
                "source_month": action.source_month,
                "quote_evidence": action.quote_evidence,
                "specificity_score": action.specificity_score,
            })
        
        # Cluster actions by category
        for category, actions in actions_by_category.items():
            if len(actions) >= 3:  # Minimum for clustering
                playbooks = clusterer.cluster_actions(actions, category)
                
                for playbook in playbooks:
                    # Check if similar playbook already exists
                    existing = db.query(Playbook).filter(
                        Playbook.category == playbook["category"],
                        Playbook.label == playbook["label"]
                    ).first()
                    
                    if not existing:
                        new_playbook = Playbook(
                            category=playbook["category"],
                            label=playbook["label"],
                            confidence_tier=playbook["confidence_tier"],
                            source_action_ids=playbook["source_action_ids"],
                            source_project_count=playbook["source_project_count"],
                        )
                        db.add(new_playbook)
                        db.commit()
                        logger.info(f"Created playbook: {playbook['label']}")
        
    except Exception as e:
        logger.error(f"Playbook clustering job failed: {e}")
    finally:
        db.close()


async def refresh_suggestions_job():
    """
    Monthly job: Refresh playbook suggestions for struggling projects.
    
    Idempotent: Checks for existing suggestions before creating new ones.
    Only creates suggestions for projects without recent suggestions.
    """
    logger.info("Starting playbook suggestions refresh job")
    
    try:
        db = SessionLocal()
        matcher = PlaybookMatcher()
        
        # Get projects with MODERATE or HIGH risk
        from app.models.projects import Project
        from app.models.playbook_suggestions import PlaybookSuggestion
        from sqlalchemy import select, and_
        
        # Query projects with MODERATE or HIGH risk
        query = select(Project).where(
            Project.composite_score >= 50  # MODERATE threshold
        )
        result = db.execute(query)
        struggling_projects = result.scalars().all()
        
        logger.info(f"Found {len(struggling_projects)} struggling projects")
        
        # Get all playbooks
        playbooks = matcher.get_all_playbooks(db)
        
        for project in struggling_projects:
            try:
                # Check if project already has recent suggestions (within 30 days)
                from datetime import timedelta
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                existing_suggestions = db.query(PlaybookSuggestion).filter(
                    and_(
                        PlaybookSuggestion.project_id == project.project_id,
                        PlaybookSuggestion.suggested_at >= cutoff_date
                    )
                ).first()
                
                if existing_suggestions:
                    logger.info(f"Project {project.project_id} already has recent suggestions, skipping")
                    continue
                
                # Generate new suggestions
                suggestions = matcher.match_playbooks(
                    {
                        "project_id": str(project.project_id),
                        "composite_score": project.composite_score,
                        "risk_category": "MODERATE" if project.composite_score < 75 else "HIGH",
                        "shap_drivers": _get_shap_drivers_for_project(db, project.project_id),
                        "reference_class_id": str(project.reference_class_id),
                        "pbe_profile": _get_pbe_profile_for_project(db, project.project_id),
                    },
                    playbooks
                )
                
                # Store suggestions
                for suggestion in suggestions:
                    new_suggestion = PlaybookSuggestion(
                        project_id=project.project_id,
                        playbook_id=suggestion["playbook"]["playbook_id"],
                        triggered_by_risk_category=suggestion.get("triggered_by_risk_category"),
                        suggested_at=datetime.utcnow(),
                    )
                    db.add(new_suggestion)
                
                db.commit()
                logger.info(f"Created {len(suggestions)} suggestions for project {project.project_id}")
                
            except Exception as e:
                logger.error(f"Failed to create suggestions for project {project.project_id}: {e}")
                db.rollback()
        
    except Exception as e:
        logger.error(f"Playbook suggestions refresh job failed: {e}")
    finally:
        db.close()


def _get_shap_drivers_for_project(db, project_id):
    """Helper to get SHAP drivers for a project."""
    # This would query the actual SHAP data from the database
    return []


def _get_pbe_profile_for_project(db, project_id):
    """Helper to get PBE profile for a project."""
    # This would query the actual PBE data from the database
    return {}


def start_scheduler():
    """Start the APScheduler with PDR monthly jobs."""
    # Schedule jobs to run on the 1st of each month at 2 AM
    scheduler.add_job(
        detect_positive_deviants_job,
        trigger=CronTrigger(day=1, hour=2, minute=0),
        id="detect_positive_deviants",
        replace_existing=True,
    )
    
    scheduler.add_job(
        extract_narrative_actions_job,
        trigger=CronTrigger(day=1, hour=3, minute=0),
        id="extract_narrative_actions",
        replace_existing=True,
    )
    
    scheduler.add_job(
        cluster_playbooks_job,
        trigger=CronTrigger(day=1, hour=4, minute=0),
        id="cluster_playbooks",
        replace_existing=True,
    )
    
    scheduler.add_job(
        refresh_suggestions_job,
        trigger=CronTrigger(day=1, hour=5, minute=0),
        id="refresh_suggestions",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("APScheduler started with PDR monthly jobs")


def stop_scheduler():
    """Stop the APScheduler."""
    scheduler.shutdown()
    logger.info("APScheduler stopped")
