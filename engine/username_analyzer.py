"""
Username & Profile Correlation Analysis Engine
Detects username patterns, alias similarity, bio keyword overlap,
and cross-platform consistency. Simulates OSINT reconnaissance.
CEH-Compliant: No actual account access or authentication bypass.
"""

import re
import hashlib
import math
import random
from typing import Dict, List, Tuple
from collections import Counter


# Common platform username patterns
PLATFORM_PATTERNS = {
    "LinkedIn": {
        "format": "firstname-lastname", "max_length": 100,
        "icon": "💼", "color": "#0A66C2",
        "base_url": "https://linkedin.com/in/"
    },
    "Twitter/X": {
        "format": "@handle", "max_length": 15,
        "icon": "🐦", "color": "#1DA1F2",
        "base_url": "https://twitter.com/"
    },
    "Instagram": {
        "format": "username", "max_length": 30,
        "icon": "📷", "color": "#E4405F",
        "base_url": "https://instagram.com/"
    },
    "GitHub": {
        "format": "username", "max_length": 39,
        "icon": "🐙", "color": "#333333",
        "base_url": "https://github.com/"
    },
    "Reddit": {
        "format": "u/username", "max_length": 20,
        "icon": "🤖", "color": "#FF4500",
        "base_url": "https://reddit.com/user/"
    },
    "Facebook": {
        "format": "profile.name", "max_length": 50,
        "icon": "📘", "color": "#1877F2",
        "base_url": "https://facebook.com/"
    },
    "TikTok": {
        "format": "@username", "max_length": 24,
        "icon": "🎵", "color": "#010101",
        "base_url": "https://tiktok.com/@"
    },
    "Discord": {
        "format": "username#0000", "max_length": 32,
        "icon": "💬", "color": "#5865F2",
        "base_url": "https://discord.com/users/"
    },
    "YouTube": {
        "format": "@channel", "max_length": 30,
        "icon": "📺", "color": "#FF0000",
        "base_url": "https://youtube.com/@"
    },
    "Pinterest": {
        "format": "username", "max_length": 30,
        "icon": "📌", "color": "#E60023",
        "base_url": "https://pinterest.com/"
    },
    "Twitch": {
        "format": "username", "max_length": 25,
        "icon": "🎮", "color": "#9146FF",
        "base_url": "https://twitch.tv/"
    },
}


class UsernameAnalyzer:
    """Analyzes usernames for cross-platform correlation patterns."""

    def analyze(self, username: str, bio: str = "", profile_url: str = "", 
                location: str = "", occupation: str = "", education: str = "") -> Dict:
        """Full username and profile analysis pipeline."""
        try:
            username = username.strip()
            
            # [FIX] Handle-Driven Seed
            # If the input name itself is a URL, or if a separate Profile URL is provided,
            # we must use the HANDLE as the master seed for everything.
            master_handle = username
            if "http" in username or "www." in username:
                 extracted = self._extract_username_from_url(username)
                 if extracted:
                     master_handle = extracted
            elif profile_url:
                extracted = self._extract_username_from_url(profile_url)
                if extracted:
                    master_handle = extracted

            if not master_handle:
                return {"status": "error", "message": "Username/Handle cannot be empty"}

            # Analyze patterns and aliases based on the MASTER handle
            pattern_analysis = self._analyze_username_patterns(master_handle)
            alias_generation = self._generate_possible_aliases(master_handle)
            
            # Generate persona and search platforms based on the MASTER handle
            target_persona = self._generate_consistent_persona(master_handle, bio, location, occupation, education)
            platform_search = self._simulate_platform_search(master_handle, target_persona, profile_url)
            
            bio_analysis = self._analyze_bio(bio) if bio else None
            url_analysis = self._analyze_profile_url(profile_url) if profile_url else None

            # Cross-platform data aggregation
            aggregated_data = self._aggregate_platform_data(master_handle, platform_search)

            # Compute correlation scores
            correlation_score = self._compute_correlation_score(
                pattern_analysis, platform_search, bio_analysis
            )

            return {
                "status": "success",
                "username": master_handle,
                "pattern_analysis": pattern_analysis,
                "possible_aliases": alias_generation,
                "platform_matches": platform_search,
                "bio_analysis": bio_analysis,
                "url_analysis": url_analysis,
                "aggregated_profile": aggregated_data,
                "correlation_score": correlation_score,
                "analysis_summary": self._generate_summary(
                    master_handle, pattern_analysis, platform_search, correlation_score
                ),
            }
        except Exception as e:
            return {"status": "error", "message": f"Username analysis failed: {str(e)}"}

    def _generate_consistent_persona(self, username: str, input_bio: str = "", 
                                   location: str = "", occupation: str = "", education: str = "") -> Dict:
        """Generate a consistent persona (Name, Job, Location) based on the username seed & inputs."""
        # Seed random with normalized username to ensure same username always gets same persona
        # Normalization: lower case, strip whitespace, remove common separators
        normalized_seed = re.sub(r"[^a-z0-9]", "", username.lower())
        rng = random.Random(hash(normalized_seed))

        # Infer name from username
        # [MODIFIED] Enforce input name priority if it looks like a name
        # If the input username has no numbers/special chars, treat it as the Real Name.
        cleaned_input = re.sub(r"[._-]", " ", username).strip()
        
        # Heuristic: If it looks like a name (alphabetical, reasonable length), use it AS IS.
        if not any(char.isdigit() for char in cleaned_input) and len(cleaned_input) > 2:
             display_name = cleaned_input.title()
        else:
            # Fallback (old logic) only if username is cryptic like "user123"
            name_parts = re.split(r"[._\-\d]+", username)
            name_parts = [p.capitalize() for p in name_parts if len(p) > 2]
            
            if len(name_parts) >= 2:
                display_name = f"{name_parts[0]} {name_parts[1]}"
            elif len(name_parts) == 1:
                display_name = name_parts[0]
            else:
                display_name = rng.choice(["Alex Doe", "Chris Smith", "Jordan Taylor", "Casey Lee"])

        # [NEW] Smart Bio/Job Inference from Handle Keywords
        # e.g. "farhan_design" -> Graphic Designer
        lower_handle = username.lower()
        
        job_keywords = {
            "design": "Graphic Designer", "art": "Digital Artist", "dev": "Software Engineer", 
            "code": "Full Stack Developer", "tech": "IT Consultant", "fit": "Fitness Coach",
            "photo": "Photographer", "music": "Musician", "writer": "Content Writer",
            "blog": "Blogger", "game": "Streamer", "play": "Gamer", "security": "Cybersecurity Analyst",
            "hack": "Penetration Tester", "crypto": "Crypto Trader", "invest": "Financial Analyst",
            "student": "Student", "learn": "Researcher", "coach": "Life Coach", "cook": "Chef"
        }
        
        inferred_job = None
        for key, role in job_keywords.items():
             if key in lower_handle:
                 inferred_job = role
                 break
                 
        # Determine job/role (influenced by inputs)
        job = occupation if occupation else (inferred_job if inferred_job else rng.choice([
            "Software Engineer", "Digital Artist", "Marketing Manager", "Student",
            "Freelance Developer", "Photojournalist", "Data Analyst", "Consultant"
        ]))
        
        # Determine location
        loc = location if location else rng.choice([
            "San Francisco, CA", "New York, NY", "London, UK", "Austin, TX", 
            "Berlin, Germany", "Dubai, UAE", "Toronto, Canada", "Singapore"
        ])

        # Education string
        edu_str = f" | Studied at {education}" if education else ""

        return {
            "display_name": display_name,
            "job": job,
            "location": loc,
            "education": education,
            "bio_template": f"{job} based in {loc}. Passionate about technology and innovation.{edu_str}"
        }

    def _extract_username_from_url(self, url: str) -> str:
        """Extract username more robustly from various URL formats."""
        try:
            # Remove protocol and www
            clean_url = re.sub(r"^https?://(www\.)?", "", url.lower())
            
            # Remove query parameters
            clean_url = clean_url.split("?")[0]
            clean_url = clean_url.rstrip("/")

            # Handle specific platform patterns
            if "youtube.com/channel/" in clean_url:
                return clean_url.split("youtube.com/channel/")[1]
            if "youtube.com/@" in clean_url:
                return clean_url.split("youtube.com/@")[1]
            if "linkedin.com/in/" in clean_url:
                return clean_url.split("linkedin.com/in/")[1]
            if "reddit.com/user/" in clean_url:
                return clean_url.split("reddit.com/user/")[1]
            
            # Generic extraction (last part of path)
            parts = clean_url.split("/")
            return parts[-1] if parts else ""
        except Exception:
            return ""

    def _analyze_username_patterns(self, username: str) -> Dict:
        """Detect structural patterns in the username."""
        patterns_found = []

        if re.search(r"\d{2,4}$", username):
            patterns_found.append({"pattern": "Trailing numbers", "detail": "May indicate birth year", "risk": "Medium"})
        if re.search(r"[._-]", username):
            patterns_found.append({"pattern": "Separator characters", "detail": "Common in real-name-based usernames", "risk": "High"})
        if re.search(r"^[a-z]+[A-Z]", username):
            patterns_found.append({"pattern": "CamelCase", "detail": "Suggests deliberate naming convention", "risk": "Medium"})
        if re.search(r"(official|real|the|iam|its)", username.lower()):
            patterns_found.append({"pattern": "Authenticity prefix", "detail": "Common when primary username was taken", "risk": "High"})
        if len(username) < 6:
            patterns_found.append({"pattern": "Short username", "detail": "Early adopter or common name", "risk": "Low"})

        name_parts = re.split(r"[._\-\d]+", username)
        name_parts = [p for p in name_parts if len(p) > 1]

        return {
            "username_length": len(username),
            "has_numbers": bool(re.search(r"\d", username)),
            "has_special_chars": bool(re.search(r"[._\-]", username)),
            "is_all_lowercase": username == username.lower(),
            "patterns_detected": patterns_found,
            "possible_name_components": name_parts,
            "uniqueness_score": self._compute_uniqueness(username),
            "predictability": "High" if len(patterns_found) > 2 else "Medium" if len(patterns_found) > 0 else "Low",
        }

    def _generate_possible_aliases(self, username: str) -> Dict:
        """Generate possible alias variations."""
        base = re.sub(r"[._\-\d]+", "", username.lower())
        parts = re.split(r"[._\-]+", username.lower())
        parts = [p for p in parts if p]

        aliases = set()
        aliases.add(username.lower())
        aliases.add(base)

        for sep in [".", "_", "-", ""]:
            if len(parts) > 1:
                aliases.add(sep.join(parts))

        nums = re.findall(r"\d+", username)
        no_nums = re.sub(r"\d+", "", username.lower())
        aliases.add(no_nums)
        for n in nums:
            aliases.add(f"{no_nums}{n}")

        aliases.discard(username.lower())

        return {
            "base_username": base,
            "components": parts,
            "generated_aliases": sorted(list(aliases))[:15],
            "total_variations": len(aliases),
            "search_expansion_note": "An attacker would search these variations across platforms",
        }

    def _simulate_platform_search(self, username: str, persona: Dict, input_profile_url: str = "") -> List[Dict]:
        """Simulate searching for the username across platforms."""
        # Use normalized seed for consistent platform selection
        normalized_seed = re.sub(r"[^a-z0-9]", "", username.lower())
        rng = random.Random(hash(normalized_seed))

        results = []
        platforms_list = list(PLATFORM_PATTERNS.items())
        rng.shuffle(platforms_list)
        
        # [IMPROVEMENT] If we have a specific input URL, we want to ensure we check 
        # ALL major platforms to find linked accounts.
        if input_profile_url:
            majors = ["Facebook", "Twitter/X", "Instagram", "LinkedIn", "GitHub"]
            # Filter majors to the front and ensure they are within num_found
            majors_found = [p for p in platforms_list if p[0] in majors]
            others = [p for p in platforms_list if p[0] not in majors]
            
            # Combine: Majors first, then shuffle others
            platforms_to_check = majors_found + others
            
            # num_found should at least cover the majors
            num_found = max(rng.randint(5, 8), len(majors))
            search_list = platforms_to_check[:num_found]
        else:
            num_found = rng.randint(4, 7)
            search_list = platforms_list[:num_found]

        # [FIX] Restore match probability logic
        has_specific_input = bool(persona.get("education") or persona.get("job") != "Software Engineer" or persona.get("location") != "San Francisco, CA")
        base_match_prob = 0.95 if has_specific_input else 0.85

        for i, (platform, info) in enumerate(search_list):
            is_input_platform = input_profile_url and platform.lower() in input_profile_url.lower()
            if input_profile_url and is_input_platform:
                print(f"DEBUG: Found input platform {platform} in {input_profile_url}")
            # [FIX] Global Seed Locking
            # If we have an input URL (e.g. instagram.com/farhan), use "farhan" as the master handle 
            # for ALL other platforms. This simulates "Linked Accounts" behavior.
            derived_username = username
            if input_profile_url:
                extracted_handle = self._extract_username_from_url(input_profile_url)
                if extracted_handle:
                    derived_username = extracted_handle
            
            if is_input_platform:
                exact_match = True
                confidence = 100.0
                profile_url = input_profile_url
                found_username = derived_username
            else:
                # If we have an input LINK, we assume the user uses this handle everywhere
                # So we force exact match probability to be extremely high (98%) for major platforms
                is_major = platform in ["Facebook", "Twitter/X", "Instagram", "LinkedIn", "GitHub"]
                
                if input_profile_url and is_major:
                    exact_match_prob = 0.98 
                else:
                    exact_match_prob = base_match_prob
                    
                exact_match = rng.random() < exact_match_prob
                
                # [FIX] Restore confidence calculation
                confidence = round(rng.uniform(70, 99), 1) if exact_match else round(rng.uniform(40, 75), 1)

                if exact_match:
                    found_username = derived_username # Use the handle from the URL!
                else:
                    found_username = self._mutate_username(username, rng)

                profile_url = f"{info['base_url']}{found_username}"

            display_name = persona["display_name"]
            bio_text = persona["bio_template"]
            
            # Platform specific bio truncation
            if platform == "Twitter/X" or platform == "Instagram":
                 bio_text = bio_text[:100]

            platform_data = {
                "platform": platform,
                "icon": info["icon"],
                "color": info["color"],
                "username_found": found_username,
                "profile_url": profile_url,
                "exact_match": exact_match,
                "confidence": confidence,
                "profile_public": rng.choice([True, True, True, False]),
                "account_age_estimate": f"{rng.randint(1, 8)} years",
                "activity_level": rng.choice(["Very Active", "Active", "Moderate"]),
                "gathered_data": {
                    "display_name": display_name,
                    "bio_available": True,
                    "bio_text": bio_text,
                    "profile_image_available": rng.choice([True, True, True, False]),
                    "location_visible": True,
                    "location": persona["location"],
                    "connections_count": rng.choice([None, f"{rng.randint(50, 5000)}+"]),
                    "posts_public": rng.choice([True, True, False]),
                    "joined_date": f"20{rng.randint(16, 24)}-{rng.randint(1,12):02d}",
                    "verification_status": rng.choice([False, False, False, True]),
                },
            }
            results.append(platform_data)


            
            
        # Force add input platform if not found
        if input_profile_url:
            found = False
            for r in results:
                if r["platform"].lower() in input_profile_url.lower():
                    found = True
                    break
            
            if not found:
                 target_platform = "Unknown"
                 target_info = {"icon": "🔗", "color": "#666", "base_url": ""}
                 for name, info in PLATFORM_PATTERNS.items():
                     clean_name = name.lower().replace(" ", "").replace("/", "") 
                     clean_input = input_profile_url.lower().replace(".", "")
                     if clean_name in clean_input:
                         target_platform = name
                         target_info = info
                         break
                 
                 results.insert(0, {
                    "platform": target_platform,
                    "icon": target_info["icon"],
                    "color": target_info["color"],
                    "username_found": username, # [bug?] should use extracted handle?
                    "profile_url": input_profile_url,
                    "exact_match": True,
                    "confidence": 100.0,
                    "profile_public": True,
                    "activity_level": "Active",
                    "gathered_data": {
                        "display_name": persona["display_name"],
                        "bio_available": True,
                        "bio_text": persona["bio_template"],
                        "location": persona["location"],
                        "location_visible": True, 
                        "connections_count": "Unknown",
                    }
                 })

        results.sort(key=lambda r: r["confidence"], reverse=True)
        return results

    def _aggregate_platform_data(self, username: str, platform_matches: List[Dict]) -> Dict:
        """Aggregate data gathered from all platforms."""
        total_platforms = len(platform_matches)
        exact_matches = sum(1 for p in platform_matches if p["exact_match"])
        public_profiles = sum(1 for p in platform_matches if p["profile_public"])

        bio_count = sum(1 for p in platform_matches if p["gathered_data"].get("bio_available"))
        image_count = sum(1 for p in platform_matches if p["gathered_data"].get("profile_image_available"))
        location_count = sum(1 for p in platform_matches if p["gathered_data"].get("location_visible"))
        posts_count = sum(1 for p in platform_matches if p["gathered_data"].get("posts_public"))

        return {
            "total_platforms_found": total_platforms,
            "exact_username_matches": exact_matches,
            "public_profiles": public_profiles,
            "data_exposure_summary": {
                "bios_available": f"{bio_count}/{total_platforms}",
                "profile_images_available": f"{image_count}/{total_platforms}",
                "locations_visible": f"{location_count}/{total_platforms}",
                "public_posts": f"{posts_count}/{total_platforms}",
            },
            "digital_footprint_size": "Large" if total_platforms > 5 else "Medium",
            "cross_platform_consistency": round(exact_matches / max(total_platforms, 1) * 100, 1),
            "aggregation_note": "Data aggregated from public simulations",
        }

    def _analyze_bio(self, bio: str) -> Dict:
        """Analyze bio text for information leakage patterns."""
        if not bio.strip():
            return None

        words = bio.lower().split()
        word_count = len(words)

        categories = {
            "profession": bool(re.search(r"(developer|engineer|designer|manager|ceo|cto|founder|student|professor|doctor|analyst|consultant)", bio.lower())),
            "location": bool(re.search(r"(based in|from|living in|located|city|country|\b[A-Z][a-z]+,\s*[A-Z]{2}\b)", bio)),
            "education": bool(re.search(r"(university|college|alumni|graduate|phd|mba|degree|student)", bio.lower())),
            "interests": bool(re.search(r"(love|passionate|enthusiast|fan of|hobby|enjoy)", bio.lower())),
            "contact": bool(re.search(r"(email|@|contact|dm|reach)", bio.lower())),
            "employer": bool(re.search(r"(at @|@\w+|working at|employed)", bio.lower())),
        }

        leaked_categories = [k for k, v in categories.items() if v]

        return {
            "word_count": word_count,
            "information_categories_detected": categories,
            "leaked_categories": leaked_categories,
            "information_density": len(leaked_categories),
            "leakage_risk": "High" if len(leaked_categories) >= 3 else "Medium" if len(leaked_categories) >= 1 else "Low",
        }

    def _analyze_profile_url(self, url: str) -> Dict:
        platform = "Unknown"
        for p_name in PLATFORM_PATTERNS:
            if p_name.lower().replace("/", "").replace(" ", "") in url.lower().replace(".", ""):
                platform = p_name
                break
        
        extracted_username = url.rstrip("/").split("/")[-1] if "/" in url else url

        return {
            "url": url,
            "detected_platform": platform,
            "extracted_username": extracted_username,
            "uses_custom_url": not any(char.isdigit() for char in extracted_username),
        }

    def _compute_correlation_score(self, pattern_analysis: Dict, platform_matches: List[Dict], bio_analysis: Dict) -> Dict:
        """Compute cross-platform correlation confidence score."""
        score = 20
        if pattern_analysis["predictability"] == "High": score += 20
        elif pattern_analysis["predictability"] == "Medium": score += 10

        exact = sum(1 for m in platform_matches if m["exact_match"])
        score += min(30, exact * 8)

        high_conf = sum(1 for m in platform_matches if m["confidence"] > 80)
        score += min(15, high_conf * 5)

        if bio_analysis and bio_analysis["leakage_risk"] == "High": score += 15
        elif bio_analysis and bio_analysis["leakage_risk"] == "Medium": score += 8

        score = min(98, score)

        return {
            "score": score,
            "level": "Critical" if score > 80 else "High" if score > 60 else "Medium" if score > 40 else "Low",
            "description": self._get_correlation_description(score),
        }

    def _compute_uniqueness(self, username: str) -> int:
        length_score = min(30, len(username) * 3)
        char_diversity = len(set(username.lower())) / max(len(username), 1) * 40
        has_special = 15 if re.search(r"[._\-]", username) else 0
        has_numbers = 10 if re.search(r"\d", username) else 0
        return min(100, int(length_score + char_diversity + has_special + has_numbers))

    def _mutate_username(self, username: str, rng) -> str:
        mutations = [
            lambda u: u + str(rng.randint(1, 99)),
            lambda u: u.replace(".", "_") if "." in u else u + "_",
            lambda u: u + "_official",
        ]
        return rng.choice(mutations)(username.lower())

    def _get_correlation_description(self, score: int) -> str:
        if score > 80: return "High probability of profile linkage."
        elif score > 60: return "Strong indicators of cross-platform correlation."
        elif score > 40: return "Moderate correlation indicators."
        return "Low correlation confidence."

    def _generate_summary(self, username: str, pattern_analysis: Dict, platform_matches: List[Dict], correlation_score: Dict) -> str:
        return f"Username '{username}' correlation analysis complete. Confidence: {correlation_score['level']}."
