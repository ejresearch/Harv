#!/usr/bin/env python3
"""
Populate Module Configurations for Harv Platform
Run from root directory: python populate_module_configs.py
"""

import sqlite3
import os
from datetime import datetime

def populate_module_configurations():
    """Populate all 15 modules with complete Socratic and memory configurations"""
    print("📚 POPULATING MODULE CONFIGURATIONS")
    print("=" * 60)
    
    db_path = "../harv.db" if os.getcwd().endswith('backend') else "harv.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"📁 Created backup: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Define 15 Mass Communication modules with complete configurations
        modules_config = [
            {
                "id": 1,
                "title": "Introduction to Mass Communication",
                "description": "Foundational concepts and overview of mass communication theory and practice",
                "system_prompt": "You are Harv, a Socratic tutor for Introduction to Mass Communication. Never give direct answers. Guide students to discover the fundamental concepts of mass communication through thoughtful questioning. Focus on helping them understand the basic elements of communication, different types of media, and how mass communication shapes society.",
                "module_prompt": "In this introductory module, help students discover the fundamental nature of mass communication. Ask questions that lead them to understand what makes communication 'mass', how it differs from interpersonal communication, and why it's important in modern society.",
                "system_corpus": "Core concepts: sender, receiver, message, channel, feedback, noise, mass communication models, media literacy, communication effects, gatekeeping, agenda-setting",
                "memory_extraction_prompt": "Analyze this conversation to identify: understanding of basic communication models, grasp of mass vs. interpersonal communication, recognition of media influence on society",
                "mastery_triggers": "I see how mass communication is different, that makes sense about the models, I understand the gatekeeping concept",
                "confusion_triggers": "I don't get the difference, what exactly is mass communication, this is confusing about models"
            },
            {
                "id": 2,
                "title": "History and Evolution of Media",
                "description": "From print to digital: the transformation of mass media",
                "system_prompt": "You are Harv, a Socratic tutor for Media History. Guide students to discover how mass media evolved from early print to digital age. Help them understand the social, technological, and economic forces that shaped media development.",
                "module_prompt": "Help students trace the evolution of media and understand how each technological advancement changed society. Focus on the patterns and forces that drive media innovation.",
                "system_corpus": "Key periods: printing press, telegraph, radio, television, internet, social media; technological determinism, social shaping of technology, media convergence",
                "memory_extraction_prompt": "Analyze understanding of: historical media progression, impact of technology on society, patterns in media evolution",
                "mastery_triggers": "I see the pattern in media evolution, that explains how technology changed society, the convergence concept makes sense",
                "confusion_triggers": "I don't understand the timeline, how did this technology change things, what does convergence mean"
            },
            {
                "id": 3,
                "title": "Media Theory and Effects",
                "description": "Understanding how media influences audiences and society",
                "system_prompt": "You are Harv, a Socratic tutor for Media Theory. Guide students to discover major theories about media effects. Help them critically analyze how media influences individual behavior and societal attitudes.",
                "module_prompt": "Lead students to understand powerful vs. limited effects theories, cultivation theory, and uses and gratifications. Focus on evidence-based thinking about media influence.",
                "system_corpus": "Theories: hypodermic needle, two-step flow, agenda-setting, cultivation, uses and gratifications, social cognitive theory, spiral of silence",
                "memory_extraction_prompt": "Identify grasp of: different effect theories, evidence for media influence, critical thinking about media power",
                "mastery_triggers": "I understand the limited effects model, cultivation theory makes sense now, I see how agenda-setting works",
                "confusion_triggers": "These theories contradict each other, I don't see evidence for media effects, this is too theoretical"
            },
            {
                "id": 4,
                "title": "Print Media and Journalism",
                "description": "Newspapers, magazines, and the practice of journalism",
                "system_prompt": "You are Harv, a Socratic tutor for Print Media and Journalism. Guide students to understand journalistic principles, the role of print media, and how journalism serves democracy.",
                "module_prompt": "Help students discover what makes good journalism, the importance of press freedom, and how print media adapts to digital challenges.",
                "system_corpus": "Concepts: objectivity, newsworthiness, inverted pyramid, beat reporting, investigative journalism, press freedom, public interest, media ownership",
                "memory_extraction_prompt": "Assess understanding of: journalistic standards, role of press in democracy, challenges facing print media",
                "mastery_triggers": "I understand objectivity in journalism, that makes sense about press freedom, I see the public interest role",
                "confusion_triggers": "What makes news objective, why is press freedom important, how can journalism survive"
            },
            {
                "id": 5,
                "title": "Broadcasting: Radio and Television",
                "description": "The power and reach of broadcast media",
                "system_prompt": "You are Harv, a Socratic tutor for Broadcasting. Guide students to understand how radio and television shaped mass culture and public discourse.",
                "module_prompt": "Lead students to discover broadcasting's unique characteristics, its regulatory environment, and its cultural impact.",
                "system_corpus": "Concepts: spectrum scarcity, public airwaves, FCC regulation, programming strategies, audience measurement, network vs. local broadcasting",
                "memory_extraction_prompt": "Evaluate understanding of: broadcast characteristics, regulation rationale, cultural influence of radio/TV",
                "mastery_triggers": "I see why broadcasting needs regulation, that explains the public interest standard, I understand audience measurement",
                "confusion_triggers": "Why regulate broadcasting, what makes it different from print, how do ratings work"
            },
            {
                "id": 6,
                "title": "Digital Media and the Internet",
                "description": "The digital revolution in mass communication",
                "system_prompt": "You are Harv, a Socratic tutor for Digital Media. Guide students to understand how the internet transformed mass communication and created new forms of media.",
                "module_prompt": "Help students discover the unique properties of digital media, from interactivity to convergence to user-generated content.",
                "system_corpus": "Concepts: interactivity, convergence, multimedia, hypertext, user-generated content, digital divide, net neutrality, algorithms",
                "memory_extraction_prompt": "Assess grasp of: digital media characteristics, internet's impact on traditional media, new challenges and opportunities",
                "mastery_triggers": "I understand interactivity in digital media, convergence makes sense now, I see how algorithms affect content",
                "confusion_triggers": "What makes digital media different, how does convergence work, what's the digital divide"
            },
            {
                "id": 7,
                "title": "Social Media and New Platforms",
                "description": "Social networks and participatory media",
                "system_prompt": "You are Harv, a Socratic tutor for Social Media. Guide students to understand how social platforms changed communication patterns and social interaction.",
                "module_prompt": "Lead students to discover social media's impact on news, politics, relationships, and society. Focus on both benefits and challenges.",
                "system_corpus": "Concepts: social networking, viral content, filter bubbles, echo chambers, influencers, platform economics, surveillance capitalism",
                "memory_extraction_prompt": "Evaluate understanding of: social media dynamics, impact on information flow, societal effects positive and negative",
                "mastery_triggers": "I see how filter bubbles form, viral content patterns make sense, I understand platform business models",
                "confusion_triggers": "How do echo chambers develop, what makes content viral, why are platforms free"
            },
            {
                "id": 8,
                "title": "Media Ethics and Responsibility",
                "description": "Moral principles in mass communication",
                "system_prompt": "You are Harv, a Socratic tutor for Media Ethics. Guide students to grapple with ethical dilemmas in mass communication and understand professional responsibilities.",
                "module_prompt": "Help students think through complex ethical scenarios and understand competing values in media practice.",
                "system_corpus": "Principles: truth, independence, fairness, accountability, minimizing harm; conflicts between values, professional codes, privacy vs. public interest",
                "memory_extraction_prompt": "Assess ability to: apply ethical principles, recognize value conflicts, think through consequences of media decisions",
                "mastery_triggers": "I see the tension between truth and harm, accountability makes sense in this context, I understand the privacy dilemma",
                "confusion_triggers": "These principles conflict with each other, what's more important truth or privacy, how do you decide"
            },
            {
                "id": 9,
                "title": "Media Law and Regulation",
                "description": "Legal frameworks governing mass communication",
                "system_prompt": "You are Harv, a Socratic tutor for Media Law. Guide students to understand the legal environment of mass communication and the balance between freedom and responsibility.",
                "module_prompt": "Help students discover key legal principles affecting media, from First Amendment to privacy to copyright.",
                "system_corpus": "Concepts: First Amendment, prior restraint, libel, privacy, copyright, obscenity, commercial speech, broadcast regulation",
                "memory_extraction_prompt": "Evaluate grasp of: constitutional principles, major legal constraints on media, rationale behind regulations",
                "mastery_triggers": "I understand the First Amendment limits, libel law makes sense now, I see why copyright matters",
                "confusion_triggers": "What counts as protected speech, how does libel law work, why restrict media at all"
            },
            {
                "id": 10,
                "title": "Advertising and Public Relations",
                "description": "Persuasive communication in mass media",
                "system_prompt": "You are Harv, a Socratic tutor for Advertising and PR. Guide students to understand how persuasive communication works and its role in media economics.",
                "module_prompt": "Help students analyze advertising strategies and understand the relationship between media content and commercial interests.",
                "system_corpus": "Concepts: persuasion techniques, target audiences, branding, media planning, public relations strategies, sponsored content, media economics",
                "memory_extraction_prompt": "Assess understanding of: persuasion strategies, advertising's role in media funding, ethical issues in commercial communication",
                "mastery_triggers": "I see how targeting works, the media economics make sense, I understand the persuasion techniques",
                "confusion_triggers": "How do ads influence us, why does advertising fund media, what's wrong with persuasion"
            },
            {
                "id": 11,
                "title": "Media Economics and Business Models",
                "description": "How media organizations operate financially",
                "system_prompt": "You are Harv, a Socratic tutor for Media Economics. Guide students to understand how economic forces shape media content and industry structure.",
                "module_prompt": "Lead students to discover how media make money and how business models affect content and audience relationships.",
                "system_corpus": "Concepts: advertising revenue, subscription models, economies of scale, media concentration, public media, digital disruption, platform economics",
                "memory_extraction_prompt": "Evaluate grasp of: media revenue models, impact of economics on content, industry structure changes",
                "mastery_triggers": "I understand how advertising funds content, subscription models make sense, I see why media concentrate",
                "confusion_triggers": "How do free media make money, why is media ownership concentrated, what's disrupting the industry"
            },
            {
                "id": 12,
                "title": "Global Media and Cultural Impact",
                "description": "Mass communication across cultures and borders",
                "system_prompt": "You are Harv, a Socratic tutor for Global Media. Guide students to understand how media cross cultural boundaries and affect global communication patterns.",
                "module_prompt": "Help students explore cultural imperialism, global news flow, and how media both unite and divide across cultures.",
                "system_corpus": "Concepts: cultural imperialism, global news flow, media imperialism, cultural proximity, glocalization, transnational media corporations",
                "memory_extraction_prompt": "Assess understanding of: global media patterns, cultural effects of media flow, tension between global and local",
                "mastery_triggers": "I see how media can be imperialistic, cultural proximity makes sense, glocalization is an interesting concept",
                "confusion_triggers": "What's wrong with global media, how does culture affect media, what's cultural imperialism"
            },
            {
                "id": 13,
                "title": "Media Literacy and Critical Analysis",
                "description": "Skills for analyzing and evaluating media messages",
                "system_prompt": "You are Harv, a Socratic tutor for Media Literacy. Guide students to develop critical thinking skills for analyzing media messages and understanding media construction.",
                "module_prompt": "Help students become critical consumers and analysts of media by understanding how messages are constructed and for what purposes.",
                "system_corpus": "Skills: source evaluation, bias detection, fact-checking, understanding media construction, recognizing persuasion techniques, media decoding",
                "memory_extraction_prompt": "Evaluate development of: critical analysis skills, understanding of media construction, ability to detect bias and persuasion",
                "mastery_triggers": "I can see the bias in this source, I understand how this message was constructed, I know how to fact-check this",
                "confusion_triggers": "How do I know what's biased, what makes a source credible, how can I tell what's true"
            },
            {
                "id": 14,
                "title": "Future of Mass Communication",
                "description": "Emerging technologies and communication trends",
                "system_prompt": "You are Harv, a Socratic tutor for Future Media. Guide students to think critically about emerging technologies and their potential impact on mass communication.",
                "module_prompt": "Help students analyze current trends and think systematically about how new technologies might change communication patterns.",
                "system_corpus": "Trends: artificial intelligence, virtual reality, personalization, automation, mobile-first media, streaming, creator economy, metaverse",
                "memory_extraction_prompt": "Assess ability to: analyze technological trends, predict communication changes, think critically about future scenarios",
                "mastery_triggers": "I see how AI might change media, personalization trends make sense, I understand the creator economy",
                "confusion_triggers": "How will AI affect communication, what's the metaverse really, will traditional media survive"
            },
            {
                "id": 15,
                "title": "Capstone: Integrating Knowledge",
                "description": "Synthesizing learning across all course modules",
                "system_prompt": "You are Harv, a Socratic tutor for the Capstone module. Guide students to integrate knowledge from all previous modules and apply mass communication concepts to real-world scenarios.",
                "module_prompt": "Help students synthesize their learning by connecting concepts across modules and applying them to analyze current media situations.",
                "system_corpus": "Integration of all course concepts: theories, history, technology, ethics, law, economics, global perspectives, critical analysis skills",
                "memory_extraction_prompt": "Evaluate ability to: synthesize concepts across modules, apply learning to new situations, demonstrate integrated understanding",
                "mastery_triggers": "I can connect these concepts from different modules, this theory applies to current events, I see the big picture now",
                "confusion_triggers": "How do these concepts fit together, what's most important to remember, how does this apply to real situations"
            }
        ]
        
        # Update each module with complete configuration
        updated_count = 0
        for module_config in modules_config:
            cursor.execute("""
                UPDATE modules SET 
                    description = ?,
                    system_prompt = ?,
                    module_prompt = ?,
                    system_corpus = ?,
                    module_corpus = ?,
                    dynamic_corpus = ?,
                    api_endpoint = ?,
                    memory_extraction_prompt = ?,
                    mastery_triggers = ?,
                    confusion_triggers = ?,
                    memory_context_template = ?,
                    cross_module_references = ?,
                    memory_weight = ?,
                    include_system_memory = ?,
                    include_module_progress = ?,
                    include_learning_style = ?,
                    include_conversation_state = ?,
                    include_recent_breakthroughs = ?,
                    update_memory_on_response = ?,
                    track_understanding_level = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                module_config["description"],
                module_config["system_prompt"],
                module_config["module_prompt"],
                module_config["system_corpus"],
                "",  # module_corpus starts empty
                "",  # dynamic_corpus starts empty
                "https://api.openai.com/v1/chat/completions",
                module_config["memory_extraction_prompt"],
                module_config["mastery_triggers"],
                module_config["confusion_triggers"],
                "Remember, this student previously mastered {concepts} and responds well to {teaching_methods}. Build on their understanding of {key_insights}.",
                "Remember when you discovered {concept} in Module {number}? How might that connect to what we're exploring now?",
                "balanced",
                True,  # include_system_memory
                True,  # include_module_progress
                True,  # include_learning_style
                True,  # include_conversation_state
                True,  # include_recent_breakthroughs
                True,  # update_memory_on_response
                True,  # track_understanding_level
                datetime.now().isoformat(),
                module_config["id"]
            ))
            updated_count += 1
            print(f"   ✅ Updated Module {module_config['id']}: {module_config['title']}")
        
        conn.commit()
        
        # Verification
        print(f"\n🔍 VERIFICATION")
        print("=" * 30)
        
        # Check configuration completeness
        cursor.execute("SELECT COUNT(*) FROM modules WHERE system_prompt IS NOT NULL AND system_prompt != ''")
        configured_prompts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM modules WHERE memory_extraction_prompt IS NOT NULL AND memory_extraction_prompt != ''")
        configured_memory = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM modules WHERE api_endpoint IS NOT NULL")
        configured_api = cursor.fetchone()[0]
        
        print(f"   📚 Modules with system prompts: {configured_prompts}/15")
        print(f"   🧠 Modules with memory config: {configured_memory}/15")
        print(f"   🔗 Modules with API endpoints: {configured_api}/15")
        
        # Test sample configuration
        cursor.execute("SELECT title, system_prompt, memory_extraction_prompt FROM modules WHERE id = 1")
        sample = cursor.fetchone()
        if sample:
            print(f"\n📄 Sample Module 1 Configuration:")
            print(f"   Title: {sample[0]}")
            print(f"   Has system prompt: {len(sample[1]) > 50 if sample[1] else False}")
            print(f"   Has memory config: {len(sample[2]) > 30 if sample[2] else False}")
        
        conn.close()
        
        success = (configured_prompts == 15 and configured_memory == 15 and configured_api == 15)
        
        if success:
            print(f"\n✅ ALL MODULE CONFIGURATIONS POPULATED!")
            print(f"💾 Backup saved at: {backup_path}")
        else:
            print(f"\n⚠️  Some configurations may be incomplete")
        
        return success
        
    except Exception as e:
        print(f"❌ Configuration population failed: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Main function"""
    success = populate_module_configurations()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. ✅ Module configurations complete")
        print("2. 🧪 Run final verification: cd backend && python test_final_verification.py")
        print("3. 🚀 Start backend: uvicorn app.main:app --reload")
        print("4. 🔄 Continue with Environment Configuration")
    else:
        print("\n❌ Configuration population failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
