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
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# AI Q&A Models
class QuestionRequest(BaseModel):
    question: str
    topic_id: Optional[str] = None
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))

class QuestionResponse(BaseModel):
    answer: str
    session_id: str
    topic_title: Optional[str] = None

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    topic_id: Optional[str] = None
    question: str
    answer: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Sample psychology topics data - Comprehensive database across all psychology fields
sample_topics = [
    # BEHAVIORAL PSYCHOLOGY
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
        "title": "Operant Conditioning",
        "category": "Behavioral Psychology",
        "subcategory": "Learning Theories",
        "content": """
# Operant Conditioning

Operant conditioning, developed by B.F. Skinner, is a learning process where behavior is controlled by consequences. Unlike classical conditioning, which focuses on involuntary responses, operant conditioning deals with voluntary behaviors and their outcomes.

## Core Principles

### Reinforcement
Reinforcement increases the likelihood of a behavior occurring again. There are two types:

**Positive Reinforcement**: Adding something desirable after a behavior
- Example: Giving praise for good performance
- Increases behavior frequency

**Negative Reinforcement**: Removing something unpleasant after a behavior
- Example: Taking aspirin to eliminate a headache
- Also increases behavior frequency

### Punishment
Punishment decreases the likelihood of a behavior occurring again. There are two types:

**Positive Punishment**: Adding something unpleasant after a behavior
- Example: Giving extra chores for misbehavior
- Decreases behavior frequency

**Negative Punishment**: Removing something desirable after a behavior
- Example: Taking away TV privileges
- Decreases behavior frequency

## Schedules of Reinforcement

### Continuous Reinforcement
Every occurrence of the behavior is reinforced. Leads to rapid learning but quick extinction.

### Partial Reinforcement
Only some occurrences are reinforced. More resistant to extinction.

**Fixed Ratio (FR)**: Reinforcement after a fixed number of responses
**Variable Ratio (VR)**: Reinforcement after varying numbers of responses
**Fixed Interval (FI)**: Reinforcement after a fixed time period
**Variable Interval (VI)**: Reinforcement after varying time periods

## Applications

### Education
- Token economies in classrooms
- Immediate feedback systems
- Gradual skill building

### Therapy
- Behavior modification programs
- Treatment of phobias and addictions
- Autism intervention strategies

### Animal Training
- Pet obedience training
- Wildlife management
- Service animal preparation

## Limitations and Criticisms

### Ethical Concerns
- Use of punishment in behavior modification
- Questions about human dignity and autonomy
- Over-reliance on external rewards

### Cognitive Factors
- Doesn't account for mental processes
- Limited explanation of complex human behavior
- Ignores intrinsic motivation

## Modern Applications

Operant conditioning principles continue to influence:
- **Gamification**: Using reward systems in apps and games
- **Workplace Management**: Employee recognition programs
- **Digital Learning**: Adaptive learning platforms
- **Healthcare**: Adherence to treatment protocols

Understanding operant conditioning helps explain how consequences shape behavior and provides practical tools for behavior change in various settings.
        """,
        "difficulty_level": "introductory",
        "reading_time": 12,
        "key_concepts": ["reinforcement", "punishment", "schedules", "shaping", "extinction"],
        "related_topics": ["Classical Conditioning", "Behavior Modification", "Learning Theory"],
        "psychologists": ["B.F. Skinner", "Edward Thorndike"],
        "experiments": ["Skinner Box", "Law of Effect"]
    },
    
    # COGNITIVE PSYCHOLOGY
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
        "title": "Working Memory",
        "category": "Cognitive Psychology",
        "subcategory": "Memory Systems",
        "content": """
# Working Memory

Working memory is a cognitive system responsible for temporarily holding and manipulating information during complex cognitive tasks. Unlike short-term memory, which simply stores information, working memory actively processes and transforms data.

## Baddeley's Model of Working Memory

### Central Executive
The central executive is the supervisory component that:
- Controls attention and coordinates information
- Manages the flow of information between subsystems
- Switches between tasks and strategies
- Has limited capacity and is effortful to use

### Phonological Loop
The phonological loop processes verbal and acoustic information:
- **Phonological Store**: Holds speech-based information for 1-2 seconds
- **Articulatory Control Process**: Refreshes information through subvocal rehearsal
- Explains why we can remember phone numbers by repeating them

### Visuospatial Sketchpad
The visuospatial sketchpad handles visual and spatial information:
- Processes images, colors, shapes, and spatial relationships
- Allows mental rotation and navigation
- Important for tasks like following directions or solving puzzles

### Episodic Buffer
Added later to the model, the episodic buffer:
- Integrates information from different sources
- Links working memory to long-term memory
- Creates coherent episodes from fragmented information

## Capacity Limitations

### Miller's Magic Number
George Miller proposed that working memory can hold 7±2 items, but modern research suggests:
- The actual capacity is closer to 4±1 chunks
- Capacity varies with the type of information
- Individual differences exist in working memory span

### Duration Limitations
Information in working memory typically lasts:
- 15-30 seconds without rehearsal
- Can be extended through active maintenance
- Decays rapidly unless refreshed

## Functions of Working Memory

### Complex Cognitive Tasks
Working memory is crucial for:
- Reading comprehension
- Mathematical problem-solving
- Reasoning and decision-making
- Language comprehension and production

### Learning and Education
Working memory capacity predicts:
- Academic achievement
- Learning difficulties
- Response to educational interventions
- Ability to follow instructions

## Individual Differences

### Working Memory Span
People vary in their working memory capacity:
- High-span individuals perform better on complex tasks
- Low-span individuals may struggle with multitasking
- Capacity can be measured through various span tasks

### Age-Related Changes
Working memory shows developmental patterns:
- Increases during childhood and adolescence
- Peaks in early adulthood
- Gradually declines with aging

## Clinical Implications

### ADHD
Individuals with ADHD often show:
- Reduced working memory capacity
- Difficulties with central executive functions
- Problems with task switching and inhibition

### Learning Disabilities
Working memory deficits are associated with:
- Dyslexia and reading difficulties
- Mathematical learning disabilities
- Language processing disorders

## Enhancement and Training

### Working Memory Training
Research on improving working memory includes:
- Computerized training programs
- Mixed evidence for transfer to other tasks
- Debate about the effectiveness of training

### Strategies for Support
Practical approaches to support working memory:
- Breaking complex tasks into smaller steps
- Using external memory aids
- Reducing cognitive load
- Providing clear instructions

Working memory is fundamental to human cognition and plays a crucial role in learning, problem-solving, and daily functioning. Understanding its mechanisms and limitations helps in education, therapy, and cognitive enhancement efforts.
        """,
        "difficulty_level": "intermediate",
        "reading_time": 15,
        "key_concepts": ["central executive", "phonological loop", "visuospatial sketchpad", "episodic buffer", "capacity limitations"],
        "related_topics": ["Cognitive Load Theory", "Short-term Memory", "Executive Functions"],
        "psychologists": ["Alan Baddeley", "Graham Hitch", "George Miller"],
        "experiments": ["Working Memory Span Tasks", "Dual-task Studies"]
    },
    
    # DEVELOPMENTAL PSYCHOLOGY
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
        "title": "Piaget's Cognitive Development Theory",
        "category": "Developmental Psychology",
        "subcategory": "Cognitive Development",
        "content": """
# Piaget's Cognitive Development Theory

Jean Piaget's theory of cognitive development describes how children's thinking develops through distinct stages. His work revolutionized our understanding of child development and continues to influence education and developmental psychology.

## Core Concepts

### Schemas
Mental structures that organize knowledge and guide thinking:
- **Definition**: Organized patterns of thought or behavior
- **Function**: Help interpret and understand experiences
- **Development**: Become more complex and sophisticated over time

### Adaptation Processes

**Assimilation**: Incorporating new information into existing schemas
- Example: A child calls all four-legged animals "dogs"
- Uses current understanding to interpret new experiences

**Accommodation**: Changing schemas to fit new information
- Example: Learning that cats are different from dogs
- Requires modifying existing mental structures

**Equilibration**: Balancing assimilation and accommodation
- Drives cognitive development forward
- Creates cognitive conflict that motivates learning

## The Four Stages

### Sensorimotor Stage (Birth to 2 years)

**Key Characteristics:**
- Learning through sensory experiences and motor actions
- Development of object permanence
- Beginning of symbolic thought

**Major Achievements:**
- **Object Permanence**: Understanding that objects exist even when not visible
- **Cause and Effect**: Learning that actions have consequences
- **Symbolic Representation**: Beginning to use symbols and language

**Substages:**
1. Reflexive actions (0-1 month)
2. Primary circular reactions (1-4 months)
3. Secondary circular reactions (4-8 months)
4. Coordination of reactions (8-12 months)
5. Tertiary circular reactions (12-18 months)
6. Mental representation (18-24 months)

### Preoperational Stage (2 to 7 years)

**Key Characteristics:**
- Rapid language development
- Symbolic thinking emerges
- Egocentric perspective dominates

**Limitations:**
- **Egocentrism**: Difficulty seeing other perspectives
- **Centration**: Focusing on one aspect while ignoring others
- **Irreversibility**: Cannot mentally reverse operations
- **Animism**: Attributing life to inanimate objects

**Conservation Tasks:**
Children at this stage fail conservation tasks:
- Number: Don't understand that quantity remains constant
- Volume: Think taller containers hold more liquid
- Mass: Believe shape changes affect amount

### Concrete Operational Stage (7 to 11 years)

**Key Characteristics:**
- Logical thinking about concrete objects and situations
- Understanding of conservation
- Ability to classify and seriate

**New Abilities:**
- **Conservation**: Quantity remains constant despite changes in appearance
- **Reversibility**: Can mentally reverse operations
- **Classification**: Ability to group objects by shared characteristics
- **Seriation**: Arranging objects in logical order

**Limitations:**
- Thinking is still tied to concrete, observable phenomena
- Difficulty with abstract or hypothetical concepts
- Limited ability to think about thinking (metacognition)

### Formal Operational Stage (11+ years)

**Key Characteristics:**
- Abstract and hypothetical thinking
- Scientific reasoning
- Systematic problem-solving

**New Abilities:**
- **Hypothetical-Deductive Reasoning**: Can generate and test hypotheses
- **Abstract Thinking**: Can think about concepts not tied to concrete objects
- **Metacognition**: Thinking about thinking processes
- **Idealistic Thinking**: Can imagine perfect worlds and solutions

**Applications:**
- Mathematical reasoning
- Scientific method
- Moral reasoning
- Future planning

## Educational Implications

### Constructivist Learning
- Students actively construct knowledge
- Learning builds on prior knowledge
- Discovery learning is emphasized

### Developmental Readiness
- Instruction should match cognitive stage
- Cannot rush development through stages
- Provide appropriate challenges

### Active Learning
- Hands-on experiences promote understanding
- Encourage exploration and experimentation
- Social interaction enhances learning

## Criticisms and Limitations

### Cultural Considerations
- Theory based primarily on Western, middle-class children
- Some cultures may emphasize different cognitive skills
- Social and cultural factors influence development

### Individual Differences
- Not all children progress through stages at same rate
- Some may show capabilities across multiple stages
- Individual variation in cognitive abilities

### Modern Research Findings
- Infants may be more competent than Piaget suggested
- Development may be more gradual than stage-like
- Domain-specific development rather than general stages

## Legacy and Modern Applications

### Education
- Constructivist teaching methods
- Age-appropriate curriculum design
- Emphasis on active learning

### Child Development
- Understanding of cognitive milestones
- Assessment of developmental delays
— Parenting and childcare practices

Piaget's theory remains influential in understanding how children's thinking develops, despite some limitations. His emphasis on active construction of knowledge and developmental stages continues to inform educational practices and developmental research.
        """,
        "difficulty_level": "intermediate",
        "reading_time": 18,
        "key_concepts": ["schemas", "assimilation", "accommodation", "conservation", "egocentrism"],
        "related_topics": ["Child Development", "Educational Psychology", "Constructivism"],
        "psychologists": ["Jean Piaget", "Lev Vygotsky"],
        "experiments": ["Conservation Tasks", "Three Mountains Task"]
    },
    
    # SOCIAL PSYCHOLOGY
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
        "title": "Attribution Theory",
        "category": "Social Psychology",
        "subcategory": "Social Cognition",
        "content": """
# Attribution Theory

Attribution theory examines how people explain the causes of behavior and events. Developed by Fritz Heider and expanded by others, this theory helps us understand how we make sense of our social world and the consequences of our explanations.

## Types of Attributions

### Internal vs. External Attributions

**Internal (Dispositional) Attributions**
- Explain behavior in terms of personal characteristics
- Focus on personality traits, abilities, or attitudes
- Example: "She succeeded because she's smart"

**External (Situational) Attributions**
- Explain behavior in terms of environmental factors
- Focus on circumstances, social pressures, or luck
- Example: "She succeeded because the test was easy"

### Stable vs. Unstable Attributions

**Stable Attributions**
- Causes that are relatively permanent
- Examples: Ability, personality traits
- Lead to expectations of consistency

**Unstable Attributions**
- Causes that can change over time
- Examples: Effort, mood, luck
- Allow for future change

### Controllable vs. Uncontrollable Attributions

**Controllable Attributions**
- Factors that can be influenced by the person
- Examples: Effort, strategy, preparation
- Lead to responsibility and accountability

**Uncontrollable Attributions**
- Factors beyond personal control
- Examples: Ability, task difficulty, luck
- Reduce personal responsibility

## Attribution Theories and Models

### Heider's Naive Psychology
Fritz Heider proposed that people are "naive scientists" who:
- Seek to understand cause-and-effect relationships
- Want to predict and control their environment
- Use common-sense psychology to explain behavior

### Jones and Davis's Correspondent Inference Theory
Explains how we infer personality traits from behavior:
- **Correspondent Inference**: Behavior reflects underlying dispositions
- **Non-common Effects**: Focus on unique outcomes of chosen actions
- **Social Desirability**: Unexpected behaviors are more informative
- **Choice**: Freely chosen behaviors are more telling

### Kelley's Covariation Model
Uses three types of information to determine attributions:

**Consensus**: How others behave in the same situation
- High consensus = External attribution
- Low consensus = Internal attribution

**Distinctiveness**: How the person behaves in other situations
- High distinctiveness = External attribution
- Low distinctiveness = Internal attribution

**Consistency**: How the person behaves over time
- High consistency = Stable attribution
- Low consistency = Unstable attribution

### Weiner's Attribution Theory
Focuses on achievement contexts with three dimensions:
- **Locus**: Internal vs. External
- **Stability**: Stable vs. Unstable
- **Controllability**: Controllable vs. Uncontrollable

## Attribution Biases and Errors

### Fundamental Attribution Error
The tendency to:
- Overestimate internal factors when explaining others' behavior
- Underestimate situational influences
- Example: Assuming someone is late because they're irresponsible, ignoring traffic

### Actor-Observer Bias
Different attribution patterns for self vs. others:
- **Actor**: Explains own behavior with situational factors
- **Observer**: Explains others' behavior with dispositional factors
- Related to differences in information and perspective

### Self-Serving Bias
Tendency to make attributions that maintain positive self-image:
- Attribute successes to internal factors
- Attribute failures to external factors
- Protects self-esteem but can hinder learning

### Hostile Attribution Bias
Tendency to interpret ambiguous actions as hostile:
- Common in aggressive individuals
- Leads to defensive or retaliatory responses
- Can escalate conflicts unnecessarily

## Cultural Differences in Attribution

### Individualistic vs. Collectivistic Cultures

**Individualistic Cultures** (e.g., US, Western Europe):
- Emphasize personal responsibility
- More likely to make dispositional attributions
- Focus on individual traits and achievements

**Collectivistic Cultures** (e.g., East Asia, Latin America):
- Emphasize social context and relationships
- More likely to make situational attributions
- Focus on group harmony and social roles

### Research Findings
- East Asians show less fundamental attribution error
- Cultural differences in self-serving bias
- Different emphasis on effort vs. ability attributions

## Applications and Implications

### Education
**Academic Achievement**:
- Attributing failure to lack of effort (controllable) vs. lack of ability (uncontrollable)
- Growth mindset vs. fixed mindset
- Impact on motivation and persistence

**Teacher Expectations**:
- How teachers explain student performance
- Self-fulfilling prophecies
- Implications for educational equity

### Mental Health

**Depression and Attribution Styles**:
- Depressive attribution style: Internal, stable, global attributions for negative events
- Learned helplessness theory
- Cognitive therapy addresses maladaptive attributions

**Relationship Satisfaction**:
- Happy couples make positive attributions for partner's behavior
- Distressed couples show negative attribution patterns
- Therapeutic interventions target attribution patterns

### Workplace and Organizations

**Performance Evaluation**:
- Manager attributions affect employee ratings
- Impact on promotion and development decisions
- Bias in performance feedback

**Team Dynamics**:
- Attribution patterns affect group cohesion
- Blame vs. problem-solving orientations
- Leadership and accountability

## Interventions and Training

### Attribution Retraining
Programs designed to change maladaptive attribution patterns:
- Focus on effort and strategy attributions
- Reduce helplessness and improve performance
- Applications in education and therapy

### Perspective-Taking
Encouraging consideration of alternative explanations:
- Reduces fundamental attribution error
- Improves empathy and understanding
- Useful in conflict resolution

### Mindfulness and Reflection
Practices that promote awareness of attribution processes:
- Reduce automatic biased attributions
- Encourage more thoughtful explanations
- Improve interpersonal relationships

Attribution theory provides crucial insights into how we understand social behavior and the consequences of our explanations. Understanding these processes can improve decision-making, relationships, and personal well-being.
        """,
        "difficulty_level": "intermediate",
        "reading_time": 16,
        "key_concepts": ["internal attribution", "external attribution", "fundamental attribution error", "self-serving bias"],
        "related_topics": ["Social Cognition", "Cognitive Biases", "Cultural Psychology"],
        "psychologists": ["Fritz Heider", "Edward Jones", "Harold Kelley", "Bernard Weiner"],
        "experiments": ["Castro Essay Study", "Quiz Show Study"]
    },
    
    # CLINICAL PSYCHOLOGY
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
    },
    {
        "title": "Anxiety Disorders",
        "category": "Clinical Psychology",
        "subcategory": "Anxiety and Stress Disorders",
        "content": """
# Anxiety Disorders

Anxiety disorders are among the most common mental health conditions, characterized by excessive fear, worry, and avoidance behaviors. They significantly impact daily functioning and quality of life, but are highly treatable with appropriate interventions.

## Types of Anxiety Disorders

### Generalized Anxiety Disorder (GAD)

**Key Features:**
- Excessive worry about multiple life domains
- Difficulty controlling worry
- Occurs more days than not for at least 6 months
- Significant distress or impairment

**Associated Symptoms:**
- Restlessness or feeling keyed up
- Being easily fatigued
- Difficulty concentrating
- Irritability
- Muscle tension
- Sleep disturbance

### Panic Disorder

**Panic Attacks:**
Sudden episodes of intense fear with physical symptoms:
- Palpitations or accelerated heart rate
- Sweating and trembling
- Shortness of breath or feelings of choking
- Chest pain or discomfort
- Nausea or abdominal distress
- Dizziness or lightheadedness
- Derealization or depersonalization
- Fear of losing control or dying
- Numbness or tingling
- Chills or hot flashes

**Panic Disorder Criteria:**
- Recurrent unexpected panic attacks
- At least one month of concern about additional attacks
- Maladaptive changes in behavior related to attacks

### Social Anxiety Disorder (Social Phobia)

**Core Features:**
- Marked fear of social or performance situations
- Fear of negative evaluation by others
- Social situations almost always provoke anxiety
- Avoidance or endurance with intense distress
- Impairment in social, occupational, or other functioning

**Common Fears:**
- Public speaking
- Meeting new people
- Eating or drinking in public
- Using public restrooms
- Writing in front of others

### Specific Phobias

**Characteristics:**
- Marked fear of specific objects or situations
- Immediate anxiety response to phobic stimulus
- Recognition that fear is excessive (in adults)
- Avoidance or intense distress
- Impairment in functioning

**Common Types:**
- Animal phobias (spiders, snakes, dogs)
- Natural environment (storms, heights, water)
- Blood-injection-injury
- Situational (elevators, flying, enclosed spaces)

### Agoraphobia

**Definition:**
Fear of being in situations where escape might be difficult or embarrassing, or where help might not be available during a panic attack.

**Common Situations:**
- Using public transportation
- Being in open spaces
- Being in enclosed places
- Standing in line or being in crowds
- Being outside of home alone

## Etiology and Risk Factors

### Biological Factors

**Genetics:**
- Moderate heritability (30-50%)
- Family clustering of anxiety disorders
- Shared genetic vulnerabilities across anxiety disorders

**Neurobiology:**
- Overactive amygdala (fear center)
- Dysregulation in fear circuitry
- Neurotransmitter imbalances (GABA, serotonin, norepinephrine)
- HPA axis dysfunction

**Temperament:**
- Behavioral inhibition in childhood
- Negative affectivity and neuroticism
- Anxiety sensitivity

### Psychological Factors

**Cognitive Factors:**
- Catastrophic thinking
- Overestimation of threat
- Underestimation of coping ability
- Attention bias toward threat

**Learning Factors:**
- Classical conditioning (learned fear associations)
- Vicarious learning (observing others' fears)
- Information transmission (warnings about dangers)
- Operant conditioning (avoidance reinforced by anxiety reduction)

### Environmental Factors

**Childhood Experiences:**
- Overprotective or rejecting parenting
- Childhood trauma or abuse
- Early separation experiences
- Exposure to uncontrollable stressors

**Life Stressors:**
- Major life changes
- Chronic stress
- Medical illness
- Substance use

## Assessment and Diagnosis

### Clinical Interview
- Detailed symptom history
- Onset and course of symptoms
- Functional impairment assessment
- Medical and psychiatric history
- Family history of mental health conditions

### Standardized Measures
- **Beck Anxiety Inventory (BAI)**
- **Generalized Anxiety Disorder 7-item (GAD-7)**
- **Social Phobia Inventory (SPIN)**
- **Panic Disorder Severity Scale (PDSS)**

### Differential Diagnosis
Important to distinguish from:
- Medical conditions (hyperthyroidism, cardiac problems)
- Substance-induced anxiety
- Other psychiatric disorders
- Normal anxiety responses

## Treatment Approaches

### Cognitive Behavioral Therapy (CBT)

**Core Components:**
- **Psychoeducation**: Understanding anxiety and its symptoms
- **Cognitive Restructuring**: Identifying and challenging anxious thoughts
- **Exposure Therapy**: Gradual confrontation of feared situations
- **Relaxation Training**: Progressive muscle relaxation, deep breathing
- **Behavioral Experiments**: Testing the validity of catastrophic predictions

**Exposure Techniques:**
- **In Vivo Exposure**: Real-life confrontation of fears
- **Imaginal Exposure**: Mental visualization of feared scenarios
- **Interoceptive Exposure**: Deliberately inducing physical sensations
- **Virtual Reality Exposure**: Computer-generated environments

### Acceptance and Commitment Therapy (ACT)

**Key Principles:**
- Acceptance of anxious thoughts and feelings
- Mindfulness and present-moment awareness
- Values-based behavior change
- Psychological flexibility

### Pharmacotherapy

**First-Line Medications:**
- **SSRIs**: Sertraline, paroxetine, escitalopram
- **SNRIs**: Venlafaxine, duloxetine
- Generally well-tolerated with fewer side effects

**Second-Line Options:**
- **Tricyclic Antidepressants**: Imipramine, clomipramine
- **MAOIs**: For treatment-resistant cases
- **Atypical Antidepressants**: Bupropion, mirtazapine

**Benzodiazepines:**
- **Short-term use only** due to dependence risk
- Effective for acute anxiety relief
- Common medications: lorazepam, clonazepam, alprazolam
- Concerns: tolerance, withdrawal, cognitive impairment

### Combination Treatment
- CBT plus medication often most effective
- Addresses both psychological and biological aspects
- May allow for lower medication doses
- Reduces relapse rates

## Prognosis and Course

### Natural Course
- Often chronic without treatment
- Tends to fluctuate in severity
- Early onset associated with more chronic course
- Comorbidity common (depression, substance use)

### Treatment Outcomes
- CBT effective for 60-80% of patients
- Medication response rates 50-70%
- Combination treatment improves outcomes
- Relapse prevention important

## Prevention and Early Intervention

### Primary Prevention
- Stress management training
- Resilience building programs
- Early childhood interventions
- Parenting programs to reduce risk factors

### Secondary Prevention
- Early identification of symptoms
- School-based anxiety prevention programs
- Brief interventions for at-risk individuals
- Screening in primary care settings

## Special Considerations

### Children and Adolescents
- Developmental considerations in assessment
- Family involvement in treatment
- School-based interventions
- Age-appropriate exposure exercises

### Older Adults
- Medical comorbidities
- Medication interactions
- Late-onset anxiety often related to medical conditions
- Cognitive changes may affect treatment

### Cultural Factors
- Cultural expressions of anxiety vary
- Stigma may affect help-seeking
- Cultural formulation important
- Adapt treatments to cultural context

Anxiety disorders are highly treatable conditions with appropriate intervention. Early identification and evidence-based treatment can significantly improve outcomes and quality of life for individuals with these conditions.
        """,
        "difficulty_level": "advanced",
        "reading_time": 22,
        "key_concepts": ["panic attacks", "GAD", "social anxiety", "phobias", "exposure therapy"],
        "related_topics": ["Cognitive Behavioral Therapy", "Panic Disorder", "PTSD"],
        "psychologists": ["Aaron Beck", "David Clark", "David Barlow"],
        "experiments": ["Little Albert Experiment", "Fear Conditioning Studies"]
    },
    
    # NEUROPSYCHOLOGY
    {
        "title": "Neuroplasticity",
        "category": "Neuropsychology",
        "subcategory": "Brain Function",
        "content": """
# Neuroplasticity

Neuroplasticity, also known as brain plasticity, refers to the brain's remarkable ability to reorganize, adapt, and change throughout life. This fundamental property allows the nervous system to modify its structure and function in response to experience, learning, injury, and environmental demands.

## Types of Neuroplasticity

### Structural Plasticity
Physical changes in brain anatomy:
- **Synaptic Plasticity**: Changes in synaptic strength and connections
- **Dendritic Plasticity**: Growth and pruning of dendritic branches
- **Axonal Plasticity**: Sprouting of new axonal connections
- **Neurogenesis**: Birth of new neurons (primarily in hippocampus)

### Functional Plasticity
Changes in how brain regions function:
- **Cortical Remapping**: Reassignment of functions to different brain areas
- **Cross-modal Plasticity**: One sensory modality taking over another's territory
- **Compensatory Plasticity**: Alternative brain regions compensating for damaged areas

## Mechanisms of Plasticity

### Synaptic Mechanisms

**Long-term Potentiation (LTP)**:
- Persistent strengthening of synapses
- Key mechanism for learning and memory
- "Neurons that fire together, wire together"

**Long-term Depression (LTD)**:
- Persistent weakening of synapses
- Important for forgetting and synaptic homeostasis
- Prevents synaptic saturation

**Spike-timing Dependent Plasticity (STDP)**:
- Precise timing of pre and postsynaptic activity
- Determines whether synapses strengthen or weaken
- Critical for information processing

### Molecular Mechanisms

**Neurotrophic Factors**:
- **BDNF (Brain-Derived Neurotrophic Factor)**: Promotes neuronal survival and growth
- **CNTF (Ciliary Neurotrophic Factor)**: Supports neuronal development
- **NGF (Nerve Growth Factor)**: Essential for neuron maintenance

**Gene Expression Changes**:
- Activity-dependent gene transcription
- Immediate early genes (c-fos, c-jun)
- Protein synthesis for structural changes

### Cellular Mechanisms

**Glial Cell Involvement**:
- **Astrocytes**: Support synaptic function and plasticity
- **Microglia**: Synaptic pruning and immune responses
- **Oligodendrocytes**: Myelination changes

**Epigenetic Modifications**:
- DNA methylation
- Histone modifications
- Non-coding RNA regulation

## Developmental Plasticity

### Critical Periods
Time windows of heightened plasticity:
- **Visual System**: First few years of life
- **Language**: Birth to puberty
- **Social Skills**: Early childhood
- **Music**: Early to mid-childhood

### Experience-Expectant Plasticity
Brain development depends on expected environmental input:
- Basic sensory and motor systems
- Requires normal environmental stimulation
- Leads to permanent deficits if missing

### Experience-Dependent Plasticity
Brain changes based on individual experiences:
- Learning-induced modifications
- Continues throughout life
- Highly variable between individuals

## Adult Neuroplasticity

### Learning-Induced Changes

**Skill Acquisition**:
- London taxi drivers: enlarged hippocampus
- Musicians: expanded motor and auditory cortices
- Jugglers: increased visual-motor areas

**Cognitive Training**:
- Working memory training effects
- Attention training modifications
- Executive function improvements

### Environmental Enrichment

**Components of Enriched Environments**:
- Physical activity and exercise
- Social interaction and stimulation
- Cognitive challenges and novelty
- Stress reduction

**Effects on the Brain**:
- Increased neurogenesis
- Enhanced synaptic density
- Improved cognitive function
- Reduced age-related decline

## Plasticity in Response to Injury

### Stroke Recovery

**Mechanisms of Recovery**:
- **Diaschisis Resolution**: Recovery of temporarily impaired brain areas
- **Redundancy**: Parallel pathways taking over function
- **Compensatory Reorganization**: Alternative brain areas assuming functions
- **Neurogenesis**: New neurons in some brain regions

**Factors Affecting Recovery**:
- Age at time of injury
- Size and location of lesion
- Time since injury
- Rehabilitation intensity
- Environmental factors

### Spinal Cord Injury

**Plasticity Mechanisms**:
- Sprouting of intact fibers
- Strengthening of weak connections
- Circuit reorganization
- Compensatory strategies

**Rehabilitation Approaches**:
- Activity-based therapies
- Electrical stimulation
- Pharmacological interventions
- Brain-computer interfaces

## Factors Influencing Plasticity

### Age-Related Changes

**Childhood and Adolescence**:
- Highest levels of plasticity
- Extensive synaptic pruning
- Myelination continues
- Critical period effects

**Adulthood**:
- Continued but reduced plasticity
- Experience-dependent changes
- Maintenance and optimization
- Compensatory mechanisms

**Aging**:
- Decreased but present plasticity
- Compensatory brain activation
- Cognitive reserve effects
- Vulnerability to pathology

### Physical Exercise

**Mechanisms**:
- Increased BDNF production
- Enhanced neurogenesis
- Improved vascular health
- Reduced inflammation

**Effects**:
- Better cognitive function
- Reduced depression and anxiety
- Slower age-related decline
- Enhanced memory and learning

### Sleep and Plasticity

**Sleep Functions**:
- Memory consolidation
- Synaptic homeostasis
- Waste clearance
- Growth hormone release

**Sleep Deprivation Effects**:
- Impaired plasticity
- Reduced learning capacity
- Memory consolidation deficits
- Cognitive performance decline

## Clinical Applications

### Rehabilitation Medicine

**Principles**:
- Use-dependent plasticity
- Task-specific training
- Intensive practice
- Progressive challenges

**Techniques**:
- Constraint-induced movement therapy
- Functional electrical stimulation
- Virtual reality training
- Brain stimulation techniques

### Mental Health Treatment

**Depression and Anxiety**:
- Antidepressants enhance plasticity
- Psychotherapy induces brain changes
- Mindfulness training effects
- Exercise interventions

**PTSD and Trauma**:
- Memory reconsolidation
- Exposure therapy mechanisms
- Fear extinction learning
- Stress resilience building

### Educational Implications

**Learning Strategies**:
- Spaced repetition
- Interleaved practice
- Active retrieval
- Elaborative encoding

**Educational Environment**:
- Rich, stimulating classrooms
- Physical activity integration
- Social learning opportunities
- Stress reduction techniques

## Future Directions

### Enhancement Techniques

**Brain Stimulation**:
- Transcranial magnetic stimulation (TMS)
- Transcranial direct current stimulation (tDCS)
- Deep brain stimulation (DBS)
- Optogenetics (experimental)

**Pharmacological Enhancement**:
- Nootropics and cognitive enhancers
- BDNF modulators
- Neurotransmitter enhancers
- Anti-aging compounds

### Research Frontiers

**Technology Integration**:
- Brain-computer interfaces
- Neurofeedback systems
- Virtual and augmented reality
- Artificial intelligence applications

**Precision Medicine**:
- Genetic factors in plasticity
- Personalized interventions
- Biomarker development
- Individual optimization strategies

Neuroplasticity represents one of the most exciting and important discoveries in neuroscience, offering hope for recovery from brain injury, enhancement of learning and memory, and maintenance of cognitive function throughout life. Understanding and harnessing these mechanisms continues to drive innovation in medicine, education, and human enhancement.
        """,
        "difficulty_level": "advanced",
        "reading_time": 20,
        "key_concepts": ["synaptic plasticity", "LTP", "neurogenesis", "critical periods", "BDNF"],
        "related_topics": ["Learning and Memory", "Brain Development", "Stroke Recovery"],
        "psychologists": ["Donald Hebb", "Eric Kandel", "Michael Merzenich"],
        "experiments": ["Hubel and Wiesel Studies", "London Taxi Driver Study"]
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
            {"key_concepts": {"$regex": search, "$options": "i"}}
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
            {"key_concepts": {"$regex": q, "$options": "i"}},
            {"psychologists": {"$regex": q, "$options": "i"}},
            {"experiments": {"$regex": q, "$options": "i"}}
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

@api_router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """AI-powered Q&A system for psychology topics"""
    try:
        # Get topic context if topic_id is provided
        topic_context = ""
        topic_title = None
        
        if request.topic_id:
            topic = await db.psychology_topics.find_one({"id": request.topic_id})
            if topic:
                topic_title = topic["title"]
                topic_context = f"""
Topic: {topic['title']}
Category: {topic['category']}
Difficulty: {topic['difficulty_level']}
Key Concepts: {', '.join(topic.get('key_concepts', []))}
Content: {topic['content'][:1500]}...

Related Topics: {', '.join(topic.get('related_topics', []))}
Key Psychologists: {', '.join(topic.get('psychologists', []))}
"""
        
        # Create system message for the AI
        system_message = f"""You are PsychLearn AI, an expert psychology tutor and teaching assistant. You help students understand psychology concepts, theories, and research.

Instructions:
- Provide clear, accurate, and educational responses about psychology topics
- Use appropriate academic language while being accessible to students
- Include relevant examples and applications when helpful
- If asked about topics outside psychology, politely redirect to psychology-related questions
- Always be encouraging and supportive in your teaching approach

{f"Current Topic Context: {topic_context}" if topic_context else "General Psychology Q&A"}

Remember: You are here to help students learn psychology effectively."""

        # Initialize the Gemini chat
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=request.session_id,
            system_message=system_message
        ).with_model("gemini", "gemini-2.0-flash").with_max_tokens(1000)
        
        # Create user message
        user_message = UserMessage(text=request.question)
        
        # Get AI response
        ai_response = await chat.send_message(user_message)
        
        # Store the conversation in database
        chat_message = ChatMessage(
            session_id=request.session_id,
            topic_id=request.topic_id,
            question=request.question,
            answer=ai_response,
        )
        
        await db.chat_messages.insert_one(chat_message.dict())
        
        return QuestionResponse(
            answer=ai_response,
            session_id=request.session_id,
            topic_title=topic_title
        )
        
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process question")

@api_router.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id}
        ).sort("created_at", 1).to_list(100)
        
        return {"messages": [ChatMessage(**msg) for msg in messages]}
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")

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