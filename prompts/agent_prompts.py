# Agent Prompts for LinkedIn Profile Enhancer

class ContentPrompts:
    """Collection of prompts for content generation agents"""
    
    def __init__(self):
        self.headline_prompts = HeadlinePrompts()
        self.about_prompts = AboutPrompts()
        self.experience_prompts = ExperiencePrompts()
        self.general_prompts = GeneralPrompts()

class HeadlinePrompts:
    """Prompts for headline optimization"""
    
    HEADLINE_ANALYSIS = """
    Analyze this LinkedIn headline and provide improvement suggestions:
    
    Current headline: "{headline}"
    Target role: "{target_role}"
    Key skills: {skills}
    
    Consider:
    1. Keyword optimization for the target role
    2. Value proposition clarity
    3. Professional branding
    4. Character limit (120 chars max)
    5. Industry-specific terms
    
    Provide 3-5 alternative headline suggestions.
    """
    
    HEADLINE_TEMPLATES = [
        "{title} | {specialization} | {key_skills}",
        "{seniority} {title} specializing in {domain} | {achievement}",
        "{title} | Helping {target_audience} with {solution} | {technologies}",
        "{role} with {years}+ years in {industry} | {unique_value_prop}"
    ]

class AboutPrompts:
    """Prompts for about section optimization"""
    
    ABOUT_STRUCTURE = """
    Create an engaging LinkedIn About section with this structure:
    
    Profile info:
    - Name: {name}
    - Current role: {current_role}
    - Years of experience: {experience_years}
    - Key skills: {key_skills}
    - Notable achievements: {achievements}
    - Target audience: {target_audience}
    
    Structure:
    1. Hook (compelling opening line)
    2. Professional summary (2-3 sentences)
    3. Key expertise and skills
    4. Notable achievements with metrics
    5. Call to action
    
    Keep it conversational, professional, and under 2000 characters.
    """
    
    ABOUT_HOOKS = [
        "🚀 Passionate about transforming {industry} through {technology}",
        "💡 {Years} years of turning complex {domain} challenges into simple solutions",
        "🎯 Helping {target_audience} achieve {outcome} through {approach}",
        "⚡ {Achievement} specialist with a track record of {impact}"
    ]

class ExperiencePrompts:
    """Prompts for experience section optimization"""
    
    EXPERIENCE_ENHANCEMENT = """
    Enhance this work experience entry:
    
    Current description: "{description}"
    Role: {title}
    Company: {company}
    Duration: {duration}
    
    Improve by:
    1. Starting with strong action verbs
    2. Adding quantified achievements
    3. Highlighting relevant skills used
    4. Showing business impact
    5. Using bullet points for readability
    
    Target the experience for: {target_role}
    """    
    ACTION_VERBS = {
        "Leadership": ["led", "managed", "directed", "coordinated", "supervised"],
        "Achievement": ["achieved", "delivered", "exceeded", "accomplished", "attained"],
        "Development": ["developed", "created", "built", "designed", "implemented"],
        "Improvement": ["optimized", "enhanced", "streamlined", "upgraded", "modernized"],
        "Problem-solving": ["resolved", "troubleshot", "analyzed", "diagnosed", "solved"]
    }

class GeneralPrompts:
    """General prompts for profile enhancement"""
    
    SKILLS_OPTIMIZATION = """
    Optimize this skills list for the target role:
    
    Current skills: {current_skills}
    Target role: {target_role}
    Job description keywords: {job_keywords}
    
    Provide:
    1. Priority ranking of current skills
    2. Missing skills to add
    3. Skills to remove or deprioritize
    4. Skill categories organization
    """
    
    KEYWORD_OPTIMIZATION = """
    Analyze keyword optimization for this profile:
    
    Profile content: {profile_content}
    Target job description: {job_description}
    
    Identify:
    1. Current keyword density
    2. Missing important keywords
    3. Over-optimized keywords
    4. Natural integration suggestions
    5. Industry-specific terminology gaps
    """
    
    PROFILE_AUDIT = """
    Conduct a comprehensive LinkedIn profile audit:
    
    Profile data: {profile_data}
    Target role: {target_role}
    Industry: {industry}
    
    Audit areas:
    1. Profile completeness (%)
    2. Keyword optimization
    3. Content quality and engagement potential
    4. Professional branding consistency
    5. Call-to-action effectiveness
    6. Visual elements (photo, banner) recommendations
    
    Provide actionable improvement suggestions with priority levels.
    """

class AnalysisPrompts:
    """Prompts for profile analysis"""
    
    COMPETITIVE_ANALYSIS = """
    Compare this profile against industry standards:
    
    Profile: {profile_data}
    Industry: {industry}
    Seniority level: {seniority}
    
    Analyze:
    1. Profile completeness vs industry average
    2. Keyword usage vs competitors
    3. Content quality benchmarks
    4. Engagement potential indicators
    5. Areas of competitive advantage
    6. Improvement opportunities
    """
    
    CONTENT_QUALITY = """
    Assess content quality across this LinkedIn profile:
    
    Profile sections: {profile_sections}
    
    Evaluate:
    1. Clarity and readability
    2. Professional tone consistency
    3. Value proposition strength
    4. Quantified achievements presence
    5. Industry relevance
    6. Call-to-action effectiveness
    
    Rate each section 1-10 and provide specific improvement suggestions.
    """

class JobMatchingPrompts:
    """Prompts for job matching analysis"""
    
    JOB_MATCH_ANALYSIS = """
    Analyze how well this profile matches the job requirements:
    
    Profile: {profile_data}
    Job description: {job_description}
    
    Match analysis:
    1. Skills alignment (%)
    2. Experience relevance
    3. Keyword overlap
    4. Education/certification fit
    5. Overall match score
    
    Provide specific recommendations to improve match score.
    """
    
    TAILORING_SUGGESTIONS = """
    Suggest profile modifications to better match this opportunity:
    
    Current profile: {profile_data}
    Target job: {job_description}
    Match score: {current_match_score}
    
    Prioritized suggestions:
    1. High-impact changes (immediate wins)
    2. Medium-impact improvements
    3. Long-term development areas
    4. Skills to highlight/add
    5. Content restructuring recommendations
    """

# Utility functions for prompt formatting
def format_prompt(template: str, **kwargs) -> str:
    """Format prompt template with provided variables"""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return f"Error formatting prompt: Missing variable {e}"

def get_prompt_by_category(category: str, prompt_name: str) -> str:
    """Get a specific prompt by category and name"""
    prompt_classes = {
        'headline': HeadlinePrompts(),
        'about': AboutPrompts(),
        'experience': ExperiencePrompts(),
        'general': GeneralPrompts(),
        'analysis': AnalysisPrompts(),
        'job_matching': JobMatchingPrompts()
    }
    
    prompt_class = prompt_classes.get(category.lower())
    if not prompt_class:
        return f"Category '{category}' not found"
    
    prompt = getattr(prompt_class, prompt_name.upper(), None)
    if not prompt:
        return f"Prompt '{prompt_name}' not found in category '{category}'"
    
    return prompt
