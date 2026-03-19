#!/usr/bin/swift
import Vision
import Foundation
import AppKit

/// macOS Vision Framework OCR helper for Xiaohongshu image-to-text extraction.
/// Usage: swift ocr_helper.swift <image_path> [image_path2 ...]
/// Output: recognized text lines to stdout, separated by "---" between images.

func recognizeText(in imagePath: String) -> [String] {
    guard let image = NSImage(contentsOfFile: imagePath) else {
        fputs("ERROR: Cannot load image: \(imagePath)\n", stderr)
        return []
    }

    guard let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        fputs("ERROR: Cannot convert to CGImage: \(imagePath)\n", stderr)
        return []
    }

    var recognizedLines: [(String, CGFloat)] = []
    let semaphore = DispatchSemaphore(value: 0)

    let request = VNRecognizeTextRequest { request, error in
        defer { semaphore.signal() }

        if let error = error {
            fputs("ERROR: OCR failed for \(imagePath): \(error.localizedDescription)\n", stderr)
            return
        }

        guard let observations = request.results as? [VNRecognizedTextObservation] else {
            return
        }

        for observation in observations {
            guard let candidate = observation.topCandidates(1).first else { continue }
            // Use the y coordinate of the bounding box (inverted: Vision uses bottom-left origin)
            let yPosition = observation.boundingBox.origin.y
            recognizedLines.append((candidate.string, yPosition))
        }
    }

    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en"]
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
    } catch {
        fputs("ERROR: Vision request failed for \(imagePath): \(error.localizedDescription)\n", stderr)
        return []
    }

    semaphore.wait()

    // Sort by y position descending (top to bottom in image coordinates)
    recognizedLines.sort { $0.1 > $1.1 }

    return recognizedLines.map { $0.0 }
}

// Main
let args = CommandLine.arguments
guard args.count > 1 else {
    fputs("Usage: swift ocr_helper.swift <image_path> [image_path2 ...]\n", stderr)
    exit(1)
}

let imagePaths = Array(args.dropFirst())

for (index, path) in imagePaths.enumerated() {
    if index > 0 {
        print("---")
    }
    let lines = recognizeText(in: path)
    for line in lines {
        print(line)
    }
}
