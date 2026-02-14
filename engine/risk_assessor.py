"""
Social Engineering Exposure Risk Assessor
Evaluates the ease of social engineering attacks based on
correlated OSINT data. Produces CEH-safe risk reports.
"""

from typing import Dict, List, Optional
from datetime import datetime


class RiskAssessor:
    """Assesses social engineering exposure risk from correlated OSINT data."""

    # Attack vector templates (educational)
    ATTACK_VECTORS = {
        "pretexting": {
            "name": "Pretexting Attack",
            "icon": "🎭",
            "description": "Building a fabricated scenario using gathered personal details",
            "required_data": ["profession", "employer", "interests"],
        },
        "spear_phishing": {
            "name": "Spear Phishing",
            "icon": "🎯",
            "description": "Crafting targeted phishing using platform-specific information",
            "required_data": ["profile_image_available", "display_name", "bio_available"],
        },
        "impersonation": {
            "name": "Profile Impersonation",
            "icon": "👤",
            "description": "Creating fake profiles using reused images and consistent usernames",
            "required_data": ["profile_image_available", "display_name"],
        },
        "trust_exploitation": {
            "name": "Trust Exploitation",
            "icon": "🤝",
            "description": "Leveraging mutual connections and platform consistency to build trust",
            "required_data": ["connections_count", "posts_public"],
        },
        "credential_inference": {
            "name": "Credential Inference",
            "icon": "🔑",
            "description": "Guessing passwords/security answers from public personal data",
            "required_data": ["location_visible", "interests", "education"],
        },
    }

    def assess(self, correlation_data: Dict, image_data: Optional[Dict] = None, username_data: Optional[Dict] = None) -> Dict:
        """Produce a comprehensive risk assessment report."""
        try:
            correlation_score = correlation_data.get("correlation_confidence", {}).get("score", 0)
            combined_platforms = correlation_data.get("combined_platform_intelligence", [])

            # Assess each attack vector
            attack_assessments = self._assess_attack_vectors(
                correlation_data, image_data, username_data
            )

            # Calculate overall risk
            overall_risk = self._calculate_overall_risk(
                correlation_score, attack_assessments, combined_platforms
            )

            # Generate platform-specific risks
            platform_risks = self._assess_platform_risks(combined_platforms)

            # Generate defensive recommendations
            recommendations = self._generate_recommendations(
                overall_risk, attack_assessments, combined_platforms
            )

            # Build the full report
            report = {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "overall_risk": overall_risk,
                "attack_vector_assessment": attack_assessments,
                "platform_risk_breakdown": platform_risks,
                "defensive_recommendations": recommendations,
                "exposure_metrics": self._compute_exposure_metrics(
                    correlation_data, image_data, username_data
                ),
                "ceh_compliance": {
                    "standard": "CEH Code of Ethics",
                    "classification": "Educational / Defensive Assessment",
                    "disclaimer": "This report assesses exposure RISK based on public data patterns. "
                                  "It does not confirm identity, access private data, or enable attacks. "
                                  "For educational and defensive cybersecurity awareness only.",
                },
                "executive_summary": self._generate_executive_summary(
                    overall_risk, attack_assessments, combined_platforms
                ),
            }

            return report

        except Exception as e:
            return {"status": "error", "message": f"Risk assessment failed: {str(e)}"}

    def _assess_attack_vectors(
        self, correlation_data: Dict, image_data: Optional[Dict], username_data: Optional[Dict]
    ) -> List[Dict]:
        """Assess feasibility of each social engineering attack vector."""
        assessments = []
        combined_platforms = correlation_data.get("combined_platform_intelligence", [])

        # Gather all available data points
        available_data = set()
        for platform in combined_platforms:
            for key, value in platform.get("data_points", {}).items():
                if value and value != "Redacted (CEH-Safe)":
                    available_data.add(key)

        # Check image data
        if image_data and image_data.get("status") == "success":
            if image_data.get("face_detection", {}).get("has_profile_photo_characteristics"):
                available_data.add("profile_image_available")

        # Check username/bio data
        if username_data and username_data.get("status") == "success":
            bio = username_data.get("bio_analysis")
            if bio:
                for cat in bio.get("leaked_categories", []):
                    available_data.add(cat)

        for vector_id, vector in self.ATTACK_VECTORS.items():
            required = set(vector["required_data"])
            matched = required & available_data
            feasibility = len(matched) / max(len(required), 1) * 100

            # Adjust based on correlation strength
            corr_score = correlation_data.get("correlation_confidence", {}).get("score", 0)
            feasibility = min(98, feasibility * 0.6 + corr_score * 0.4)

            risk_level = (
                "Critical" if feasibility > 80
                else "High" if feasibility > 60
                else "Medium" if feasibility > 40
                else "Low"
            )

            assessments.append({
                "vector_id": vector_id,
                "name": vector["name"],
                "icon": vector["icon"],
                "description": vector["description"],
                "feasibility_score": round(feasibility, 1),
                "risk_level": risk_level,
                "data_requirements_met": f"{len(matched)}/{len(required)}",
                "available_data": list(matched),
                "missing_data": list(required - matched),
                "mitigation": self._get_vector_mitigation(vector_id),
            })

        assessments.sort(key=lambda a: a["feasibility_score"], reverse=True)
        return assessments

    def _calculate_overall_risk(
        self, correlation_score: int, attack_assessments: List[Dict], combined_platforms: List[Dict]
    ) -> Dict:
        """Calculate overall social engineering exposure risk."""
        # Average of attack vector scores
        avg_attack = sum(a["feasibility_score"] for a in attack_assessments) / max(len(attack_assessments), 1)
        max_attack = max((a["feasibility_score"] for a in attack_assessments), default=0)

        # Platform exposure
        critical_platforms = sum(1 for p in combined_platforms if p.get("combined_risk") == "Critical")
        high_platforms = sum(1 for p in combined_platforms if p.get("combined_risk") == "High")

        # Weighted overall
        overall = (
            correlation_score * 0.35 +
            avg_attack * 0.25 +
            max_attack * 0.20 +
            min(100, (critical_platforms * 15 + high_platforms * 8)) * 0.20
        )
        overall = min(98, int(overall))

        return {
            "score": overall,
            "level": self._score_to_level(overall),
            "color": self._score_to_color(overall),
            "headline": self._get_risk_headline(overall),
            "description": self._get_risk_description(overall),
        }

    def _assess_platform_risks(self, combined_platforms: List[Dict]) -> List[Dict]:
        """Generate risk assessment per platform."""
        risks = []
        for platform in combined_platforms:
            score = platform.get("combined_score", 0)
            data_points = platform.get("data_points", {})
            exposed_count = sum(1 for v in data_points.values() if v and v != "Redacted (CEH-Safe)" and v is not None)

            risks.append({
                "platform": platform["platform"],
                "icon": platform.get("icon", "🌐"),
                "color": platform.get("color", "#666"),
                "risk_level": platform.get("combined_risk", "Unknown"),
                "combined_score": score,
                "data_points_exposed": exposed_count,
                "total_data_points": len(data_points),
                "exposure_ratio": f"{exposed_count}/{len(data_points)}",
                "key_exposures": [k for k, v in data_points.items() if v and v != "Redacted (CEH-Safe)" and v is not None],
            })

        return risks

    def _generate_recommendations(
        self, overall_risk: Dict, attack_assessments: List[Dict], combined_platforms: List[Dict]
    ) -> List[Dict]:
        """Generate defensive recommendations based on findings."""
        recs = []

        score = overall_risk["score"]

        # Always recommend
        recs.append({
            "priority": "High",
            "category": "Username Hygiene",
            "icon": "🔐",
            "recommendation": "Use unique, unrelated usernames across different platforms to prevent cross-platform correlation.",
            "impact": "Reduces profile linkage risk by up to 60%",
        })

        if score > 40:
            recs.append({
                "priority": "High",
                "category": "Image Diversity",
                "icon": "🖼️",
                "recommendation": "Avoid reusing the same profile photo across platforms. Use platform-specific images.",
                "impact": "Prevents image-based cross-platform matching",
            })

        if score > 50:
            recs.append({
                "priority": "Critical",
                "category": "Bio Information Control",
                "icon": "📝",
                "recommendation": "Minimize personal details in public bios. Avoid listing employer, exact role, or location together.",
                "impact": "Reduces spear-phishing and pretexting attack surface",
            })

        if score > 60:
            recs.append({
                "priority": "Critical",
                "category": "Privacy Settings Audit",
                "icon": "⚙️",
                "recommendation": "Review and tighten privacy settings on all social media platforms. Limit public visibility.",
                "impact": "Directly reduces publicly available attack surface",
            })

        recs.append({
            "priority": "Medium",
            "category": "Two-Factor Authentication",
            "icon": "🛡️",
            "recommendation": "Enable 2FA on all accounts to protect against credential-based attacks.",
            "impact": "Prevents account compromise even if credentials are guessed",
        })

        critical_vectors = [a for a in attack_assessments if a["risk_level"] == "Critical"]
        if critical_vectors:
            recs.append({
                "priority": "Critical",
                "category": "Immediate Action Required",
                "icon": "🚨",
                "recommendation": f"Critical risk detected for: {', '.join(v['name'] for v in critical_vectors)}. Immediate privacy hardening recommended.",
                "impact": "Addresses the most severe exposure vectors",
            })

        recs.append({
            "priority": "Medium",
            "category": "Regular OSINT Self-Assessment",
            "icon": "🔍",
            "recommendation": "Periodically search for your own information online to monitor your digital footprint exposure.",
            "impact": "Enables proactive identification and remediation of information leaks",
        })

        return recs

    def _compute_exposure_metrics(
        self, correlation_data: Dict, image_data: Optional[Dict], username_data: Optional[Dict]
    ) -> Dict:
        """Compute quantified exposure metrics for dashboard display."""
        combined = correlation_data.get("combined_platform_intelligence", [])

        total_platforms = len(combined)
        critical = sum(1 for p in combined if p.get("combined_risk") == "Critical")
        high = sum(1 for p in combined if p.get("combined_risk") == "High")

        total_data_points = sum(
            sum(1 for v in p.get("data_points", {}).values() if v and v != "Redacted (CEH-Safe)" and v is not None)
            for p in combined
        )

        return {
            "platforms_exposed": total_platforms,
            "critical_platforms": critical,
            "high_risk_platforms": high,
            "total_data_points_exposed": total_data_points,
            "digital_footprint_score": min(100, total_platforms * 12 + total_data_points * 3),
            "attack_surface_area": f"{total_data_points} data points across {total_platforms} platforms",
        }

    def _get_vector_mitigation(self, vector_id: str) -> str:
        mitigations = {
            "pretexting": "Limit professional details in public profiles. Verify unexpected contacts through independent channels.",
            "spear_phishing": "Be suspicious of highly personalized emails. Verify sender identity through alternative communication.",
            "impersonation": "Use unique images per platform. Set up alerts for your name/username mentions online.",
            "trust_exploitation": "Verify connection requests independently. Be cautious of unsolicited professional contacts.",
            "credential_inference": "Use strong, unique passwords. Avoid security questions based on public information.",
        }
        return mitigations.get(vector_id, "Review and tighten privacy settings across all platforms.")

    def _score_to_level(self, score: int) -> str:
        if score > 80: return "Critical"
        elif score > 60: return "High"
        elif score > 40: return "Medium"
        return "Low"

    def _score_to_color(self, score: int) -> str:
        if score > 80: return "#FF1744"
        elif score > 60: return "#FF9100"
        elif score > 40: return "#FFD600"
        return "#00E676"

    def _get_risk_headline(self, score: int) -> str:
        if score > 80:
            return "⚠️ CRITICAL: Severe Social Engineering Exposure Detected"
        elif score > 60:
            return "🔶 HIGH: Significant Exposure Risk Identified"
        elif score > 40:
            return "🟡 MODERATE: Some Exposure Patterns Found"
        return "🟢 LOW: Minimal Exposure Risk"

    def _get_risk_description(self, score: int) -> str:
        if score > 80:
            return ("Multiple strong indicators suggest this digital footprint is highly vulnerable to social engineering. "
                    "An attacker could easily correlate profiles across platforms and build a convincing attack pretext. "
                    "Immediate privacy hardening measures are strongly recommended.")
        elif score > 60:
            return ("Significant patterns of cross-platform correlation and data exposure detected. "
                    "An attacker with moderate skill could link these profiles and craft targeted social engineering attacks. "
                    "Privacy settings review and information reduction recommended.")
        elif score > 40:
            return ("Some cross-platform correlation patterns exist but would require additional effort to exploit. "
                    "Basic privacy improvements would significantly reduce exposure risk.")
        return ("Limited cross-platform correlation detected. Digital footprint shows reasonable privacy practices. "
                "Minor improvements could further strengthen privacy posture.")

    def _generate_executive_summary(
        self, overall_risk: Dict, attack_assessments: List[Dict], combined_platforms: List[Dict]
    ) -> str:
        """Generate a concise executive summary for the report."""
        score = overall_risk["score"]
        level = overall_risk["level"]

        # Count critical/high vectors
        critical_attacks = [a for a in attack_assessments if a["risk_level"] in ("Critical", "High")]
        platform_count = len(combined_platforms)

        parts = [
            f"Overall Social Engineering Exposure: {level} ({score}%).",
            f"Analysis covered {platform_count} platform(s).",
        ]

        if critical_attacks:
            parts.append(
                f"Critical/High risk detected for {len(critical_attacks)} attack vector(s): "
                f"{', '.join(a['name'] for a in critical_attacks[:3])}."
            )

        parts.append(
            "High probability of profile linkage due to repeated image usage and "
            "identical usernames across platforms."
            if score > 60 else
            "Moderate correlation patterns detected across digital footprint."
            if score > 40 else
            "Limited cross-platform correlation — good privacy practices observed."
        )

        parts.append(
            "⚠️ This assessment indicates RISK levels, not confirmed identity. "
            "For educational and defensive purposes only."
        )

        return " ".join(parts)
