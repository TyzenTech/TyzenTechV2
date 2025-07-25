from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import requests
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="PsychLearn API", description="Comprehensive Psychology Learning Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class PsychologyTopic(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    category: str
    subcategory: Optional[str] = None
    content: str
    difficulty_level: str  # introductory, intermediate, advanced, graduate
    reading_time: int  # in minutes
    key_concepts: List[str] = []
    related_topics: List[str] = []
    psychologists: List[str] = []
    experiments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PsychologyTopicCreate(BaseModel):
    title: str
    category: str
    subcategory: Optional[str] = None
    content: str
    difficulty_level: str
    reading_time: int
    key_concepts: List[str] = []
    related_topics: List[str] = []
    psychologists: List[str] = []
    experiments: List[str] = []

class SearchFilters(BaseModel):
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    reading_time_max: Optional[int] = None
    psychologist: Optional[str] = None

class UserNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic_id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic_id: str
    status: str  # "completed", "in-progress", "bookmarked"
    progress_percentage: int = 0
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

# Sample psychology topics data
sample_topics = [
    {
        "title": "Classical Conditioning",
        "category": "Behavioral Psychology",
        "subcategory": "Learning Theories",
        "content": """
# Classical Conditioning

Classical conditioning is a fundamental learning process discovered by Ivan Pavlov in the early 1900s. This type of learning occurs when a neutral stimulus becomes associated with a naturally occurring stimulus, eventually triggering a similar response.

## Key Components

### Unconditioned Stimulus (UCS)
The unconditioned stimulus is a stimulus that naturally and automatically triggers a response. In Pavlov's famous experiment, the food was the UCS because it naturally caused dogs to salivate.

### Unconditioned Response (UCR)
The unconditioned response is the natural reaction to the unconditioned stimulus. The dogs' salivation in response to food is an example of a UCR.

### Conditioned Stimulus (CS)
The conditioned stimulus is a previously neutral stimulus that, after being associated with the UCS, triggers a conditioned response. In Pavlov's experiment, the bell became the CS.

### Conditioned Response (CR)
The conditioned response is the learned response to the conditioned stimulus. The dogs eventually salivated when they heard the bell, even without food present.

## Real-World Applications

Classical conditioning principles are used in various therapeutic approaches:
- **Systematic Desensitization**: Treating phobias by gradually exposing patients to feared stimuli
- **Aversion Therapy**: Creating negative associations with harmful behaviors
- **Advertising**: Associating products with positive emotions or experiences

## Important Concepts

### Acquisition
The initial learning phase where the CS and UCS are paired repeatedly until the association is formed.

### Extinction
The gradual weakening of the conditioned response when the CS is repeatedly presented without the UCS.

### Spontaneous Recovery
The reappearance of a previously extinguished conditioned response after a rest period.

### Generalization
The tendency to respond to stimuli similar to the original CS.

### Discrimination
The ability to distinguish between the CS and other similar stimuli.

## Modern Research

Contemporary research has expanded our understanding of classical conditioning:
- **Biological Preparedness**: Some associations are learned more easily than others due to evolutionary factors
- **Cognitive Factors**: Mental processes influence the strength and formation of conditioned responses
- **Neural Mechanisms**: Brain imaging shows specific neural pathways involved in classical conditioning

Classical conditioning remains a cornerstone of learning theory and continues to inform therapeutic practices and our understanding of human behavior.
        """,
        "difficulty_level": "introductory",
        "reading_time": 8,
        "key_concepts": ["UCS", "UCR", "CS", "CR", "acquisition", "extinction", "generalization"],
        "related_topics": ["Operant Conditioning", "Behavioral Therapy", "Learning Theory"],
        "psychologists": ["Ivan Pavlov", "John Watson"],
        "experiments": ["Pavlov's Dogs", "Little Albert Experiment"]
    },
    {
        "title": "Cognitive Load Theory",
        "category": "Cognitive Psychology",
        "subcategory": "Memory and Learning",
        "content": """
# Cognitive Load Theory

Cognitive Load Theory, developed by John Sweller, explains how the human cognitive system processes information and the implications for learning and instruction. The theory is based on our understanding of working memory limitations and long-term memory structures.

## Types of Cognitive Load

### Intrinsic Load
This is the inherent difficulty associated with the material itself. It relates to the complexity of the information and cannot be altered by instructional design. For example, learning basic arithmetic has lower intrinsic load than learning calculus.

### Extraneous Load
This refers to the cognitive load imposed by the way information is presented. Poor instructional design can increase extraneous load unnecessarily, hindering learning. Examples include:
- Unclear explanations
- Irrelevant information
- Poor organization of material

### Germane Load
This is the cognitive effort devoted to processing, constructing, and automating schemas. Unlike extraneous load, germane load is beneficial for learning as it contributes to meaningful understanding and knowledge construction.

## Working Memory Limitations

Working memory can only hold approximately 7±2 pieces of information simultaneously (Miller's Magic Number). However, when dealing with novel information, this capacity is even more limited - often just 2-4 elements can be processed effectively.

## Long-Term Memory and Schemas

Long-term memory stores organized knowledge structures called schemas. These schemas:
- Reduce cognitive load by chunking information
- Allow for automatic processing of familiar patterns
- Enable experts to process complex information more efficiently

## Instructional Design Implications

### Worked Examples
Providing fully worked examples reduces cognitive load by showing learners the complete solution process rather than requiring them to discover it themselves.

### Progressive Problem Solving
Starting with worked examples and gradually transitioning to independent problem-solving helps manage cognitive load appropriately.

### Elimination of Redundancy
Removing unnecessary information reduces extraneous cognitive load, allowing learners to focus on essential elements.

### Modality Effect
Presenting information through multiple sensory channels (visual and auditory) can increase effective working memory capacity.

## Applications in Education

Cognitive Load Theory has significant implications for:
- **Curriculum Design**: Sequencing content from simple to complex
- **Multimedia Learning**: Optimizing the use of text, images, and audio
- **Assessment**: Designing tests that accurately measure learning without imposing unnecessary cognitive burden
- **Technology-Enhanced Learning**: Creating digital learning environments that support cognitive processing

## Research Evidence

Extensive research supports Cognitive Load Theory principles:
- Students learn more effectively when extraneous cognitive load is minimized
- Expertise reversal effect shows that instructional techniques effective for novices may be less effective or even harmful for experts
- Split-attention effect demonstrates the importance of integrating related information sources

Understanding Cognitive Load Theory helps educators and instructional designers create more effective learning experiences by aligning instruction with how the human mind processes information.
        """,
        "difficulty_level": "intermediate",
        "reading_time": 12,
        "key_concepts": ["working memory", "schemas", "intrinsic load", "extraneous load", "germane load"],
        "related_topics": ["Working Memory", "Schema Theory", "Instructional Design"],
        "psychologists": ["John Sweller", "Richard Mayer", "George Miller"],
        "experiments": ["Dual-task paradigm", "Split-attention studies"]
    },
    {
        "title": "Attachment Theory",
        "category": "Developmental Psychology",
        "subcategory": "Early Development",
        "content": """
# Attachment Theory

Attachment theory, developed by John Bowlby and Mary Ainsworth, explains the emotional bonds that develop between children and their primary caregivers. This theory has profound implications for understanding human relationships, emotional development, and mental health across the lifespan.

## Historical Development

### John Bowlby's Contributions
Bowlby, influenced by ethology and psychoanalysis, proposed that attachment behaviors are innate and serve an evolutionary function - keeping infants close to caregivers for protection and survival.

### Mary Ainsworth's Research
Ainsworth's observational studies, particularly the Strange Situation procedure, identified different patterns of attachment and provided empirical support for Bowlby's theory.

## Core Principles

### Attachment Behavioral System
Infants are born with an innate behavioral system designed to maintain proximity to caregivers. This system is activated by:
- Separation from the caregiver
- Perceived threats or danger
- Illness or fatigue
- Unfamiliar environments

### Internal Working Models
Children develop mental representations of themselves, others, and relationships based on their early attachment experiences. These models influence:
- Expectations about relationships
- Self-worth and self-concept
- Emotional regulation strategies
- Social behavior patterns

## Attachment Styles

### Secure Attachment (approximately 60-65% of children)
**Characteristics:**
- Uses caregiver as a secure base for exploration
- Shows distress when separated but is easily comforted upon reunion
- Develops positive internal working models of self and others

**Adult relationships:**
- Comfortable with intimacy and independence
- Effective communication and conflict resolution
- Higher relationship satisfaction

### Insecure-Avoidant Attachment (approximately 20-25%)
**Characteristics:**
- Shows little distress during separation
- Avoids or ignores caregiver upon reunion
- Appears independent but may suppress emotional needs

**Adult relationships:**
- Uncomfortable with closeness
- Values independence over intimacy
- May have difficulty expressing emotions

### Insecure-Ambivalent/Resistant Attachment (approximately 10-15%)
**Characteristics:**
- Shows intense distress during separation
- Difficult to comfort upon reunion
- Alternates between seeking comfort and resisting it

**Adult relationships:**
- Anxious about relationships
- Fear of abandonment
- May be perceived as clingy or demanding

### Disorganized/Disoriented Attachment (approximately 5-10%)
**Characteristics:**
- Inconsistent and contradictory behaviors
- May freeze, show stereotypical movements, or display fear of caregiver
- Often associated with trauma or inconsistent caregiving

**Adult relationships:**
- Chaotic relationship patterns
- Difficulty regulating emotions
- Higher risk for mental health issues

## Lifelong Impact

### Childhood Development
Secure attachment promotes:
- Better emotional regulation
- Higher self-esteem
- More positive peer relationships
- Greater resilience to stress

### Adult Relationships
Attachment styles influence:
- Romantic relationships
- Parenting behaviors
- Friendships and social connections
- Work relationships

### Mental Health
Insecure attachment patterns are associated with:
- Higher rates of anxiety and depression
- Personality disorders
- Difficulty in therapeutic relationships
- Increased vulnerability to trauma

## Therapeutic Applications

### Attachment-Based Therapy
- Focuses on repairing and strengthening attachment relationships
- Emphasizes the therapeutic relationship as a corrective emotional experience
- Used with individuals, couples, and families

### Parenting Interventions
- Programs designed to promote secure attachment
- Teaching sensitive and responsive caregiving
- Supporting parents who experienced insecure attachment in their own childhood

## Cultural Considerations

While attachment theory is widely applicable, cultural variations exist in:
- Caregiving practices
- Values regarding independence vs. interdependence
- Expression of attachment behaviors
- Definition of sensitive caregiving

## Current Research

Modern attachment research explores:
- Neurobiological correlates of attachment
- Epigenetic factors in attachment transmission
- Attachment in digital age relationships
- Cross-cultural attachment patterns
- Attachment in therapy and healing

Attachment theory continues to be one of the most influential frameworks for understanding human relationships and emotional development, providing valuable insights for parents, educators, therapists, and anyone interested in human connection.
        """,
        "difficulty_level": "intermediate",
        "reading_time": 15,
        "key_concepts": ["secure base", "internal working models", "strange situation", "attachment styles"],
        "related_topics": ["Child Development", "Social Psychology", "Therapeutic Relationships"],
        "psychologists": ["John Bowlby", "Mary Ainsworth", "Harry Harlow"],
        "experiments": ["Strange Situation", "Harlow's Monkey Studies"]
    },
    {
        "title": "Social Identity Theory",
        "category": "Social Psychology",
        "subcategory": "Group Behavior",
        "content": """
# Social Identity Theory

Social Identity Theory, developed by Henri Tajfel and John Turner, explains how individuals derive part of their identity from their membership in social groups. This theory has been instrumental in understanding intergroup relations, prejudice, discrimination, and social conflict.

## Core Components

### Personal Identity vs. Social Identity
**Personal Identity** consists of unique individual characteristics, personal relationships, and individual achievements.

**Social Identity** derives from membership in social groups and includes:
- Emotional significance of group membership
- Value placed on group membership
- Sense of belonging to the group

### Social Categorization
People naturally categorize themselves and others into groups based on various characteristics:
- Race and ethnicity
- Gender
- Age
- Profession
- Nationality
- Religion
- Political affiliation

This categorization simplifies the social world but can lead to stereotyping and oversimplification.

### Social Identification
Once individuals categorize themselves as group members, they:
- Adopt the group's norms and behaviors
- Develop emotional attachment to the group
- Experience the group's successes and failures as their own
- Begin to see themselves in terms of group characteristics

### Social Comparison
Groups compare themselves with other groups to evaluate their:
- Status and prestige
- Abilities and achievements
- Values and beliefs
- Resources and power

## In-Group vs. Out-Group Dynamics

### In-Group Favoritism
People tend to:
- View in-group members more positively
- Attribute positive behaviors of in-group members to internal factors
- Provide more help and resources to in-group members
- Show greater trust and cooperation with in-group members

### Out-Group Derogation
People may:
- View out-group members more negatively
- Attribute negative behaviors of out-group members to internal factors
- Show less empathy for out-group members' suffering
- Perceive out-group members as more homogeneous ("they're all the same")

## Positive Distinctiveness

Groups strive to maintain positive distinctiveness - viewing their group as better than others in meaningful ways. This can be achieved through:
- **Social Competition**: Direct competition for resources or status
- **Social Creativity**: Changing the dimensions of comparison or the values placed on different characteristics
- **Social Mobility**: Individual attempts to leave the group for a higher-status group

## Applications and Implications

### Prejudice and Discrimination
Social Identity Theory helps explain:
- How prejudice develops and persists
- Why discrimination occurs even without economic competition
- The role of group membership in perpetuating inequality
- How positive in-group identity can lead to negative out-group attitudes

### Organizational Behavior
In workplace settings, the theory explains:
- Team dynamics and loyalty
- Departmental conflicts
- Mergers and acquisitions challenges
- Diversity and inclusion initiatives

### Intergroup Conflict
The theory provides insights into:
- Ethnic and racial conflicts
- Religious tensions
- Political polarization
- International relations

## Reducing Intergroup Bias

### Contact Hypothesis
Positive intergroup contact can reduce prejudice when:
- Groups have equal status
- Common goals exist
- Cooperation is required
- Authority figures support interaction

### Superordinate Goals
Creating shared objectives that require cooperation between groups can:
- Reduce intergroup hostility
- Build positive relationships
- Create new, inclusive group identities

### Recategorization
Encouraging people to think of themselves as members of a larger, more inclusive group can reduce bias toward former out-group members.

## Criticisms and Limitations

### Individual Differences
The theory may not account for:
- Personality factors that influence group identification
- Individual differences in need for belonging
- Varying motivations for group membership

### Context Dependency
Group salience and importance can vary based on:
- Situational factors
- Cultural contexts
- Personal experiences
- Life circumstances

### Complexity of Identity
Modern individuals often have:
- Multiple group memberships
- Intersecting identities
- Changing group affiliations
- Conflicting group loyalties

## Contemporary Research

Current research in social identity explores:
- **Digital Identities**: How online communities and social media affect identity formation
- **Intersectionality**: How multiple group memberships interact
- **Globalization Effects**: How global connectivity affects local group identities
- **Neuroscience**: Brain mechanisms underlying in-group/out-group processing
- **Collective Action**: How social identity motivates social and political movements

## Practical Applications

### Education
- Designing inclusive curricula
- Reducing bullying and school segregation
- Promoting multicultural understanding
- Creating positive classroom climates

### Therapy and Counseling
- Understanding identity-related mental health issues
- Working with clients from marginalized groups
- Addressing internalized oppression
- Building positive group identity

### Public Policy
- Designing integration programs
- Addressing systemic discrimination
- Promoting social cohesion
- Managing diversity in institutions

Social Identity Theory continues to be relevant in our increasingly diverse and interconnected world, providing valuable insights into how group membership shapes individual behavior and intergroup relations.
        """,
        "difficulty_level": "advanced",
        "reading_time": 18,
        "key_concepts": ["social categorization", "in-group favoritism", "positive distinctiveness", "intergroup bias"],
        "related_topics": ["Prejudice and Discrimination", "Group Dynamics", "Intergroup Contact"],
        "psychologists": ["Henri Tajfel", "John Turner", "Gordon Allport"],
        "experiments": ["Minimal Group Paradigm", "Robbers Cave Study"]
    },
    {
        "title": "Major Depressive Disorder",
        "category": "Clinical Psychology",
        "subcategory": "Mood Disorders",
        "content": """
# Major Depressive Disorder (MDD)

Major Depressive Disorder is one of the most common and serious mental health conditions, characterized by persistent feelings of sadness, hopelessness, and loss of interest in activities. It significantly impacts daily functioning and quality of life.

## Diagnostic Criteria (DSM-5)

To be diagnosed with MDD, an individual must experience **five or more** of the following symptoms during the same 2-week period, with at least one symptom being either (1) depressed mood or (2) loss of interest/pleasure:

### Core Symptoms
1. **Depressed mood** most of the day, nearly every day
2. **Markedly diminished interest or pleasure** in all or almost all activities (anhedonia)
3. **Significant weight loss or gain** (5% of body weight in a month) or decrease/increase in appetite
4. **Insomnia or hypersomnia** nearly every day
5. **Psychomotor agitation or retardation** observable by others
6. **Fatigue or loss of energy** nearly every day
7. **Feelings of worthlessness or inappropriate guilt** nearly every day
8. **Diminished ability to think or concentrate** or indecisiveness nearly every day
9. **Recurrent thoughts of death** or suicidal ideation

### Functional Impairment
Symptoms must cause clinically significant distress or impairment in:
- Social functioning
- Occupational performance
- Other important areas of life

## Epidemiology

### Prevalence
- **Lifetime prevalence**: Approximately 10-15% of the general population
- **12-month prevalence**: About 6-7% of adults
- **Gender differences**: Women are twice as likely as men to experience MDD
- **Age of onset**: Often begins in late teens to early twenties

### Risk Factors
**Biological:**
- Genetic predisposition (40-50% heritability)
- Neurotransmitter imbalances (serotonin, norepinephrine, dopamine)
- Hormonal changes
- Medical conditions

**Psychological:**
- Cognitive distortions
- Negative thinking patterns
- Low self-esteem
- Poor coping skills

**Social/Environmental:**
- Chronic stress
- Trauma and abuse
- Social isolation
- Socioeconomic disadvantage
- Life transitions and losses

## Neurobiological Factors

### Neurotransmitter Systems
**Monoamine Hypothesis:**
- Reduced activity of serotonin, norepinephrine, and dopamine
- Basis for many antidepressant medications
- Oversimplified but still clinically relevant

**Modern Understanding:**
- Complex interactions between multiple neurotransmitter systems
- GABA and glutamate also involved
- Neuroplasticity and brain connectivity changes

### Brain Structure and Function
**Neuroimaging findings:**
- Reduced hippocampal volume
- Decreased prefrontal cortex activity
- Hyperactive amygdala
- Altered default mode network connectivity

### HPA Axis Dysfunction
- Chronic activation of stress response system
- Elevated cortisol levels
- Disrupted circadian rhythms
- Impact on immune function

## Psychological Theories

### Cognitive Theory (Aaron Beck)
**Cognitive Triad:**
1. Negative views of self
2. Negative views of the world
3. Negative views of the future

**Common Cognitive Distortions:**
- All-or-nothing thinking
- Catastrophizing
- Mind reading
- Emotional reasoning
- Personalization

### Learned Helplessness (Martin Seligman)
- Depression results from learning that one has no control over negative events
- Leads to generalized sense of helplessness
- Basis for understanding hopelessness in depression

### Behavioral Activation Theory
- Depression maintained by reduced activity and avoidance
- Loss of positive reinforcement
- Negative feedback loops between mood and behavior

## Types and Specifiers

### Major Depressive Episodes
- Single episode
- Recurrent episodes

### Specifiers
- **With anxious distress**
- **With mixed features** (some manic symptoms)
- **With melancholic features** (severe anhedonia, worse in morning)
- **With psychotic features**
- **With catatonic features**
- **With seasonal pattern** (seasonal affective disorder)
- **With postpartum onset**

## Treatment Approaches

### Psychotherapy
**Cognitive Behavioral Therapy (CBT):**
- Most extensively researched
- Focuses on changing negative thought patterns
- Behavioral activation components
- Typically 12-20 sessions

**Interpersonal Therapy (IPT):**
- Focuses on relationship issues
- Addresses grief, disputes, transitions, deficits
- Time-limited (12-16 sessions)

**Psychodynamic Therapy:**
- Explores unconscious conflicts
- Focuses on past relationships and experiences
- Longer-term approach

### Pharmacotherapy
**First-line treatments:**
- SSRIs (Selective Serotonin Reuptake Inhibitors)
- SNRIs (Serotonin-Norepinephrine Reuptake Inhibitors)

**Second-line treatments:**
- Tricyclic antidepressants
- MAOIs (Monoamine Oxidase Inhibitors)
- Atypical antidepressants

**Considerations:**
- Trial period of 4-6 weeks
- Side effect profiles vary
- Genetic testing available for some medications

### Combination Treatment
- Psychotherapy + medication often most effective
- Addresses both psychological and biological factors
- Reduces relapse rates

### Alternative Treatments
- **Electroconvulsive Therapy (ECT)**: For severe, treatment-resistant cases
- **Transcranial Magnetic Stimulation (TMS)**: Non-invasive brain stimulation
- **Light Therapy**: Particularly for seasonal depression
- **Exercise**: Significant antidepressant effects
- **Mindfulness-Based Interventions**: Reduces relapse risk

## Course and Prognosis

### Natural Course
- Without treatment, episodes typically last 6-12 months
- High relapse rates (50-80% experience recurrent episodes)
- Earlier onset associated with more chronic course
- Residual symptoms increase relapse risk

### Treatment Response
- 60-70% respond to first antidepressant trial
- 80-90% eventually respond to some treatment
- Combination therapy improves outcomes
- Maintenance treatment reduces relapse

## Comorbidity

**Common comorbid conditions:**
- Anxiety disorders (50-70%)
- Substance use disorders (30-40%)
- Personality disorders
- Medical conditions (cardiovascular disease, diabetes)

## Prevention

### Primary Prevention
- Stress management
- Social support
- Healthy lifestyle
- Early intervention for at-risk individuals

### Relapse Prevention
- Maintenance therapy
- Recognizing early warning signs
- Continuing therapy after recovery
- Lifestyle modifications

## Suicide Risk

- 15% of individuals with severe depression die by suicide
- Higher risk factors: hopelessness, social isolation, comorbid substance use
- Assessment and safety planning essential
- Crisis intervention resources crucial

## Cultural Considerations

- Expression of depression varies across cultures
- Somatic symptoms more prominent in some cultures
- Stigma affects help-seeking behavior
- Cultural formulation important in treatment planning

Major Depressive Disorder remains a significant public health challenge, but with proper diagnosis and evidence-based treatment, most individuals can achieve significant improvement in symptoms and quality of life. Ongoing research continues to refine our understanding and treatment approaches.
        """,
        "difficulty_level": "advanced",
        "reading_time": 25,
        "key_concepts": ["anhedonia", "cognitive triad", "monoamine hypothesis", "DSM-5 criteria"],
        "related_topics": ["Cognitive Behavioral Therapy", "Bipolar Disorder", "Anxiety Disorders"],
        "psychologists": ["Aaron Beck", "Martin Seligman", "Peter Lewinsohn"],
        "experiments": ["Learned Helplessness Studies", "Cognitive Therapy Outcome Studies"]
    }
]

# Initialize sample data
@app.on_event("startup")
async def initialize_data():
    """Initialize database with sample psychology topics"""
    try:
        # Check if topics already exist
        existing_count = await db.psychology_topics.count_documents({})
        if existing_count == 0:
            # Insert sample topics
            for topic_data in sample_topics:
                topic = PsychologyTopic(**topic_data)
                await db.psychology_topics.insert_one(topic.dict())
            logging.info(f"Initialized {len(sample_topics)} sample psychology topics")
    except Exception as e:
        logging.error(f"Error initializing data: {e}")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "PsychLearn API - Comprehensive Psychology Learning Platform"}

@api_router.get("/topics", response_model=List[PsychologyTopic])
async def get_topics(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    limit: int = Query(50, description="Maximum number of topics to return")
):
    """Get psychology topics with optional filtering and search"""
    filter_query = {}
    
    if category:
        filter_query["category"] = {"$regex": category, "$options": "i"}
    
    if difficulty_level:
        filter_query["difficulty_level"] = difficulty_level
    
    if search:
        filter_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
            {"key_concepts": {"$in": [{"$regex": search, "$options": "i"}]}}
        ]
    
    topics = await db.psychology_topics.find(filter_query).limit(limit).to_list(limit)
    return [PsychologyTopic(**topic) for topic in topics]

@api_router.get("/topics/{topic_id}", response_model=PsychologyTopic)
async def get_topic(topic_id: str):
    """Get a specific psychology topic by ID"""
    topic = await db.psychology_topics.find_one({"id": topic_id})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return PsychologyTopic(**topic)

@api_router.get("/categories")
async def get_categories():
    """Get all available psychology categories"""
    categories = await db.psychology_topics.distinct("category")
    subcategories = await db.psychology_topics.distinct("subcategory")
    
    return {
        "categories": categories,
        "subcategories": subcategories,
        "difficulty_levels": ["introductory", "intermediate", "advanced", "graduate"]
    }

@api_router.get("/search")
async def search_topics(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(20)
):
    """Advanced search for psychology topics"""
    search_query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
            {"key_concepts": {"$in": [{"$regex": q, "$options": "i"}]}},
            {"psychologists": {"$in": [{"$regex": q, "$options": "i"}]}},
            {"experiments": {"$in": [{"$regex": q, "$options": "i"}]}}
        ]
    }
    
    if category:
        search_query["category"] = {"$regex": category, "$options": "i"}
    
    if difficulty:
        search_query["difficulty_level"] = difficulty
    
    topics = await db.psychology_topics.find(search_query).limit(limit).to_list(limit)
    
    return {
        "query": q,
        "total_results": len(topics),
        "results": [PsychologyTopic(**topic) for topic in topics]
    }

@api_router.post("/topics", response_model=PsychologyTopic)
async def create_topic(topic: PsychologyTopicCreate):
    """Create a new psychology topic (admin function)"""
    topic_dict = topic.dict()
    new_topic = PsychologyTopic(**topic_dict)
    await db.psychology_topics.insert_one(new_topic.dict())
    return new_topic

@api_router.get("/stats")
async def get_stats():
    """Get platform statistics"""
    total_topics = await db.psychology_topics.count_documents({})
    categories = await db.psychology_topics.distinct("category")
    
    # Count topics by category
    category_counts = {}
    for category in categories:
        count = await db.psychology_topics.count_documents({"category": category})
        category_counts[category] = count
    
    # Count by difficulty level
    difficulty_counts = {}
    for level in ["introductory", "intermediate", "advanced", "graduate"]:
        count = await db.psychology_topics.count_documents({"difficulty_level": level})
        difficulty_counts[level] = count
    
    return {
        "total_topics": total_topics,
        "total_categories": len(categories),
        "topics_by_category": category_counts,
        "topics_by_difficulty": difficulty_counts
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()