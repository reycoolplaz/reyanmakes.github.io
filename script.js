const projectData = {
    lakehouse: {
        title: "The Lake House",
        description: "A multi-room fort built entirely from reclaimed materials and trash. This structure survived multiple storms and floods, proving that resourcefulness and solid design can outlast expensive materials.",
        story: "What started as a simple shelter became an ongoing project to build a multi-room structure using only materials I could find or salvage. I learned to work with what nature and the neighborhood provided — old pallets, discarded lumber, scrap metal for supports. The biggest challenge was making it weatherproof and structurally sound. Through trial and error, I figured out how to reinforce weak points and redirect water flow. Seeing it withstand its first major storm was one of my proudest moments.",
        skills: ["Woodworking", "Structural Design", "Problem Solving", "Resourcefulness", "Planning"],
        materials: "Reclaimed pallets, salvaged lumber, scrap metal, recycled tarps"
    },
    gokart: {
        title: "Go-Kart",
        description: "A fully functional go-kart welded together from scrap metal and spare parts. This project taught me metalworking, welding, and mechanical problem-solving.",
        story: "I wanted to build something that moved, so I decided on a go-kart. I scavenged metal from old furniture, used wheels from a discarded lawn mower, and taught myself MIG welding through YouTube videos and practice. The hardest part was getting the frame geometry right so it would be stable and safe. After several iterations and test runs, I had a working go-kart that could actually carry me down the street. It wasn't pretty, but it worked — and that's what mattered.",
        skills: ["MIG Welding", "Metal Fabrication", "Mechanical Engineering", "Safety Planning"],
        materials: "Scrap steel, salvaged wheels, old lawn mower parts, metal tubing"
    },
    bed: {
        title: "Custom Bed Frame",
        description: "A loft bed designed and built from scratch to maximize room space. This project combined design, precise measurements, and solid woodworking skills.",
        story: "My room was small, so I designed a loft bed to create more usable space underneath. I sketched out multiple designs before settling on one that was structurally sound and practical. The challenge was making sure it could support weight safely and fit perfectly in the space. I measured everything twice, cut once, and assembled it piece by piece. The result was a custom piece of furniture that perfectly fit my needs and is still in use today.",
        skills: ["Woodworking", "Design", "Precision Measurement", "Carpentry", "Planning"],
        materials: "Dimensional lumber, wood screws, brackets, wood stain"
    },
    canoe: {
        title: "Canoe Trailer",
        description: "A bike-mounted trailer designed to haul a canoe. This practical build combined welding, design thinking, and outdoor recreation.",
        story: "I love canoeing but didn't have an easy way to transport my canoe to the water. So I designed and built a custom trailer that could be towed by my bike. The challenge was making it lightweight enough to pull but strong enough to support the canoe. I used scrap metal for the frame, salvaged wheels, and created a simple hitch mechanism. Now I can bike to the lake with my canoe in tow — no car needed.",
        skills: ["Welding", "Design", "Problem Solving", "Mechanical Engineering"],
        materials: "Scrap metal tubing, salvaged wheels, bike hitch parts, bolts"
    },
    knife: {
        title: "Full Tang Knife",
        description: "A hand-forged knife made during winter break. This project introduced me to blacksmithing and the satisfaction of creating a tool from raw steel.",
        story: "I wanted to try blacksmithing, so I spent winter break learning to forge a knife. Starting with a piece of steel, I heated, hammered, and shaped it into a blade. The process required patience — heating the metal to the right temperature, hammering consistently, and gradually shaping the edge. After grinding and sharpening, I added a wooden handle and treated the blade. The result is a functional knife that I made entirely by hand.",
        skills: ["Blacksmithing", "Metal Shaping", "Tool Making", "Patience", "Craftsmanship"],
        materials: "High-carbon steel, wood for handle, forge, hammer, grinder"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('projectModal');
    const modalBody = document.getElementById('modalBody');
    const closeBtn = document.querySelector('.close');
    const projectCards = document.querySelectorAll('.project-card[data-project]');

    if (projectCards.length > 0 && modal) {
        projectCards.forEach(card => {
            card.addEventListener('click', () => {
                const projectId = card.getAttribute('data-project');
                const project = projectData[projectId];

                if (project) {
                    modalBody.innerHTML = `
                        <h2>${project.title}</h2>
                        <p><strong>${project.description}</strong></p>
                        <p>${project.story}</p>
                        <div class="skills-used">
                            <strong>Skills Used:</strong>
                            ${project.skills.map(skill => `<span class="tag">${skill}</span>`).join('')}
                        </div>
                        <p><strong>Materials:</strong> ${project.materials}</p>
                    `;
                    modal.style.display = 'block';
                    document.body.style.overflow = 'hidden';
                }
            });
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            });
        }

        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }

    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.startsWith('#') && href !== '#') {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    const navHeight = document.querySelector('.navbar').offsetHeight;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});
