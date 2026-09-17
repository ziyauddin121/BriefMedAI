import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import BentoFeatures from "@/components/BentoFeatures";
import HowItWorks from "@/components/HowItWorks";
import DemoSection from "@/components/DemoSection";
import TechStack from "@/components/TechStack";
import RoadmapSection from "@/components/RoadmapSection";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="relative min-h-screen">
      {/* Animated grid background */}
      <div className="grid-bg" aria-hidden="true" />

      <div className="relative z-10">
        <Header />
        <HeroSection />
        <BentoFeatures />
        <HowItWorks />
        <DemoSection />
        <TechStack />
        <RoadmapSection />
        <Footer />
      </div>
    </div>
  );
};

export default Index;
