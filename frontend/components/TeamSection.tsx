"use client";

import { motion, Variants } from "framer-motion";

const teamMembers = [
  {
    name: "Mandhir Sawarn",
    role: "Full Stack Developer & AI Engineer",
    initials: "MS",
    image: "https://i.ibb.co/H6TXftx/f7917340-171f-497d-90e4-9999ad7e2597.png",
    gradient: "from-blue-500 to-purple-600",
  },
  {
    name: "Nimish Kumar",
    role: "Backend Developer",
    initials: "NK",
    image: "/team/nimish.png",
    gradient: "from-purple-500 to-pink-600",
  },
  {
    name: "Aditya Kumar",
    role: "Frontend Developer & UI/UX",
    initials: "AK",
    image: "/team/aditya.png",
    gradient: "from-teal-400 to-blue-500",
  },
  {
    name: "Sumit Raj",
    role: "Research & Testing",
    initials: "SR",
    image: "/team/sumit.png",
    gradient: "from-orange-400 to-red-500",
  },
];

export function TeamSection() {
  const container: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.15 },
    },
  };

  const item: Variants = {
    hidden: { opacity: 0, y: 30 },
    show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <section id="team" className="relative py-24 scroll-mt-10 overflow-hidden">
      {/* Background Particles/Glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/4 w-64 h-64 bg-accent/10 rounded-full blur-[100px] -translate-y-1/2" />
        <div className="absolute top-1/2 right-1/4 w-64 h-64 bg-accent-alt/10 rounded-full blur-[100px] -translate-y-1/2" />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-5xl font-bold text-white mb-4"
          >
            Meet Our <span className="animated-gradient-text glow-text">Team</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-text-secondary text-lg max-w-2xl mx-auto"
          >
            The minds behind this AI-powered Deepfake Detection platform.
          </motion.p>
        </div>

        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-100px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {teamMembers.map((member, idx) => (
            <motion.div key={idx} variants={item} className="h-full">
              <div
                className="glass-card relative p-8 h-full flex flex-col items-center text-center group hover:-translate-y-2 transition-all duration-500 hover:shadow-[0_0_40px_rgba(108,99,255,0.15)] overflow-hidden"
                style={{
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                }}
              >
                {/* Hover gradient background effect */}
                <div className="absolute inset-0 bg-gradient-to-b from-white/[0.04] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

                {/* Thin Gradient Border Overlay on Hover */}
                <div className="absolute inset-0 rounded-[24px] pointer-events-none border border-accent/0 group-hover:border-accent/40 transition-colors duration-500" />

                <div className="relative mb-6 mt-2">
                  <div className={`w-24 h-24 rounded-full bg-gradient-to-tr ${member.gradient} p-[2px] group-hover:scale-110 transition-transform duration-500`}>
                    <div className="w-full h-full rounded-full bg-bg-primary flex items-center justify-center relative overflow-hidden">
                      {/* Subtle inner glow */}
                      <div className={`absolute inset-0 bg-gradient-to-tr ${member.gradient} opacity-20`} />
                      {member.image ? (
                        <img src={member.image} alt={member.name} className="w-full h-full object-cover relative z-10" />
                      ) : (
                        <span className="text-2xl font-bold text-white relative z-10">{member.initials}</span>
                      )}
                    </div>
                  </div>
                  {/* Online Indicator */}
                  <div className="absolute bottom-1 right-2 w-5 h-5 bg-bg-primary rounded-full flex items-center justify-center z-20">
                    <div className="w-3 h-3 bg-authentic rounded-full animate-pulse shadow-[0_0_10px_rgba(74,222,128,0.8)]" />
                  </div>
                </div>

                <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-white transition-colors duration-300 relative z-10">{member.name}</h3>
                <p className="text-sm text-text-secondary relative z-10">{member.role}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
