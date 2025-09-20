"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, Zap, Shield, Brain, Download } from "lucide-react";
import Header from "../components/atoms/Header";
import FeatureCard from "../components/atoms/FeatureCard";
import LoadingSpinner from "../components/atoms/LoadingSpinner";
import FileUpload from "../components/molecules/FileUpload";
import DataAnalysis from "../components/molecules/DataAnalysis";
import ChatInterface from "../components/molecules/ChatInterface";
import HistoryPanel from "../components/molecules/HistoryPanel";
import ErrorDisplay from "../components/molecules/ErrorDisplay";

export default function Home() {
  const [currentStep, setCurrentStep] = useState<
    "upload" | "analyze" | "fix" | "download"
  >("upload");
  const [uploadData, setUploadData] = useState<any>(null);
  console.log("🚀 ~ Home ~ uploadData:", uploadData);
  const [analysisData, setAnalysisData] = useState<any>(null);
  console.log("🚀 ~ Home ~ analysisData:", analysisData);
  const [fixData, setFixData] = useState<any>(null);
  console.log("🚀 ~ Home ~ fixData:", fixData);
  const [isLoading, setIsLoading] = useState(false);
  console.log("🚀 ~ Home ~ isLoading:", isLoading);
  const [loadingMessage, setLoadingMessage] = useState("Processing...");
  const [showChat, setShowChat] = useState(false);
  console.log("🚀 ~ Home ~ showChat:", showChat);
  const [showHistory, setShowHistory] = useState(false);
  console.log("🚀 ~ Home ~ showHistory:", showHistory);

  const features = [
    {
      icon: <Upload className="w-8 h-8 text-primary-600" />,
      title: "Flexible Data Input",
      description: "Support for CSV, Excel, JSON, and database connections",
    },
    {
      icon: <Shield className="w-8 h-8 text-success-600" />,
      title: "Quality Detection",
      description:
        "Automatically identify missing values, duplicates, and inconsistencies",
    },
    {
      icon: <Zap className="w-8 h-8 text-warning-600" />,
      title: "Automated Fixes",
      description: "Smart corrections while preserving data integrity",
    },
    {
      icon: <Brain className="w-8 h-8 text-primary-600" />,
      title: "AI-Driven Insights",
      description: "Intelligent recommendations and anomaly detection",
    },
    {
      icon: <FileText className="w-8 h-8 text-gray-600" />,
      title: "Data Lineage",
      description: "Visual history of transformations and fixes",
    },
    {
      icon: <Download className="w-8 h-8 text-success-600" />,
      title: "Clean Delivery",
      description: "Download cleaned datasets or integrate with BI tools",
    },
  ];

  const handleUploadComplete = (data: any) => {
    setUploadData(data);
    setIsLoading(true);
    setLoadingMessage("Preparing data for analysis...");
    setTimeout(() => {
      setIsLoading(false);
      setCurrentStep("analyze");
    }, 500); // Brief loading transition
  };

  const handleAnalysisComplete = (data: any) => {
    setAnalysisData(data);
    setIsLoading(true);
    setLoadingMessage("Preparing fix recommendations...");
    setTimeout(() => {
      setIsLoading(false);
      setCurrentStep("fix");
    }, 500); // Brief loading transition
  };

  const handleFixComplete = (data: any) => {
    setIsLoading(true);
    setLoadingMessage("Applying fixes and cleaning data...");
    // Simulate processing time for fixes
    setTimeout(() => {
      setFixData(data);
      setIsLoading(false);
      setCurrentStep("download");
    }, 1500); // Longer delay for fix processing
  };

  return (
    <div className="min-h-screen">
      <Header
        onChatClick={() => setShowChat(!showChat)}
        onHistoryClick={() => setShowHistory(!showHistory)}
      />

      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl font-bold text-gradient mb-6">Data Doctor</h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            An intelligent system that detects, fixes, and delivers clean,
            reliable data. Transform messy datasets into analytics-ready
            information with AI-powered insights.
          </p>

          {/* Feature Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <FeatureCard {...feature} />
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Main Workflow */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="max-w-4xl mx-auto"
        >
          {/* Progress Steps */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              {[
                { key: "upload", label: "Upload", icon: Upload },
                { key: "analyze", label: "Analyze", icon: FileText },
                { key: "fix", label: "Fix", icon: Zap },
                { key: "download", label: "Download", icon: Download },
              ].map((step, index) => {
                const Icon = step.icon;
                const isActive = currentStep === step.key;
                const isCompleted =
                  ["upload", "analyze", "fix"].indexOf(currentStep) >
                  ["upload", "analyze", "fix"].indexOf(step.key);

                return (
                  <div key={step.key} className="flex items-center">
                    <div
                      className={`
                      flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300
                      ${
                        isActive
                          ? "bg-primary-600 border-primary-600 text-white"
                          : isCompleted
                          ? "bg-success-600 border-success-600 text-white"
                          : "bg-white border-gray-300 text-gray-400"
                      }
                    `}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <span
                      className={`ml-2 font-medium ${
                        isActive
                          ? "text-primary-600"
                          : isCompleted
                          ? "text-success-600"
                          : "text-gray-400"
                      }`}
                    >
                      {step.label}
                    </span>
                    {index < 3 && (
                      <div
                        className={`w-8 h-0.5 mx-4 ${
                          isCompleted ? "bg-success-600" : "bg-gray-300"
                        }`}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Step Content */}
          <div className="card p-8">
            {isLoading && (
              <div className="flex flex-col justify-center items-center py-12">
                <LoadingSpinner />
                <p className="mt-4 text-gray-600 dark:text-gray-300">
                  {loadingMessage}
                </p>
              </div>
            )}

            {!isLoading && currentStep === "upload" && (
              <FileUpload onComplete={handleUploadComplete} />
            )}

            {!isLoading && currentStep === "analyze" && uploadData && (
              <DataAnalysis
                uploadData={uploadData}
                onComplete={handleAnalysisComplete}
              />
            )}

            {!isLoading && currentStep === "fix" && analysisData && (
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-4">Apply Data Fixes</h2>
                <p className="text-gray-600 mb-6">
                  Review the detected issues and apply automated fixes to clean
                  your data.
                </p>
                <button
                  onClick={() => handleFixComplete({})}
                  className="btn-primary"
                  disabled={isLoading}
                >
                  {isLoading ? "Applying Fixes..." : "Apply Fixes"}
                </button>
              </div>
            )}

            {!isLoading && currentStep === "download" && fixData && (
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-4">Download Clean Data</h2>
                <p className="text-gray-600 mb-6">
                  Your data has been cleaned and is ready for download.
                </p>
                <button className="btn-primary">
                  Download Cleaned Dataset
                </button>
              </div>
            )}
          </div>
        </motion.div>
      </main>

      {/* Chat Interface */}
      {showChat && (
        <ChatInterface
          onClose={() => setShowChat(false)}
          uploadData={uploadData}
          analysisData={analysisData}
          fixData={fixData}
        />
      )}

      {/* History Panel */}
      {showHistory && <HistoryPanel onClose={() => setShowHistory(false)} />}

      {/* Error Display */}
      <ErrorDisplay position="top-right" />
    </div>
  );
}
