// concat_cuts.swift — LOCAL, FREE hard-cut assembly: N clips concatenated + one audio bed, 1280x720.
// Repository tool generalised from projects/la-pomme/production/scene-01/concat_cuts.swift
// (identical behaviour). No model, no network, no generation; AVFoundation only (no ffmpeg).
// Build: swiftc -O -o /tmp/concat_cuts tools/edit/concat_cuts.swift
// Usage: concat_cuts <project_root> <out.mp4> <audio.wav> <clip1.mp4> ... <clipN.mp4>
// Relative paths resolve against <project_root>; refuses to overwrite <out.mp4>.
import AVFoundation
import Foundation

let args = CommandLine.arguments
guard args.count >= 5 else { fputs("usage: concat_cuts root out rain clips...\n", stderr); exit(2) }
let root = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2], relativeTo: root).absoluteURL
let rainURL = URL(fileURLWithPath: args[3], relativeTo: root).absoluteURL
let clips = args[4...].map { URL(fileURLWithPath: $0, relativeTo: root).absoluteURL }
if FileManager.default.fileExists(atPath: outURL.path) { fputs("refuse to overwrite \(outURL.path)\n", stderr); exit(2) }

let comp = AVMutableComposition()
guard let vTrack = comp.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
      let aTrack = comp.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) else { exit(3) }
var cursor = CMTime.zero
var report: [[String: Any]] = []
let sem = DispatchSemaphore(value: 0)
Task {
  do {
    for url in clips {
      let asset = AVURLAsset(url: url)
      let dur = try await asset.load(.duration)
      guard let src = try await asset.loadTracks(withMediaType: .video).first else { fputs("no video in \(url.path)\n", stderr); exit(2) }
      try vTrack.insertTimeRange(CMTimeRange(start: .zero, duration: dur), of: src, at: cursor)
      report.append(["clip": url.lastPathComponent, "start_s": cursor.seconds, "duration_s": dur.seconds])
      cursor = cursor + dur
    }
    let rain = AVURLAsset(url: rainURL)
    let rainDur = try await rain.load(.duration)
    if let ra = try await rain.loadTracks(withMediaType: .audio).first {
      let take = CMTimeMinimum(rainDur, cursor)
      try aTrack.insertTimeRange(CMTimeRange(start: .zero, duration: take), of: ra, at: .zero)
    }
    guard let ex = AVAssetExportSession(asset: comp, presetName: AVAssetExportPreset1280x720) else { exit(3) }
    ex.outputURL = outURL; ex.outputFileType = .mp4
    await ex.export()
    if ex.status != .completed { fputs("export failed: \(String(describing: ex.error))\n", stderr); exit(3) }
    let out: [String: Any] = ["output": outURL.path, "total_duration_s": cursor.seconds, "clips": report, "audio": rainURL.lastPathComponent]
    let data = try JSONSerialization.data(withJSONObject: out, options: [.prettyPrinted])
    print(String(data: data, encoding: .utf8)!)
  } catch { fputs("error: \(error)\n", stderr); exit(3) }
  sem.signal()
}
sem.wait()
