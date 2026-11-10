//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
/// \file SteppingAction.cc
/// \brief Implementation of the B4a::SteppingAction class

#include "SteppingAction.hh"

#include "DetectorConstruction.hh"
#include "EventAction.hh"

#include "G4AnalysisManager.hh"
#include "G4Event.hh"
#include "G4RunManager.hh"
#include "G4Step.hh"
#include "G4SystemOfUnits.hh"
#include "globals.hh"

using namespace B4;

namespace B4a
{

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

SteppingAction::SteppingAction(const DetectorConstruction* detConstruction,
                               EventAction* eventAction)
  : fDetConstruction(detConstruction), fEventAction(eventAction)
{}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

void SteppingAction::UserSteppingAction(const G4Step* step)
{
  // Collect energy and track length step by step

  // get volume of the current step
  auto volume = step->GetPreStepPoint()->GetTouchableHandle()->GetVolume();

  // energy deposit
  auto edep = step->GetTotalEnergyDeposit();

  // step length
  G4double stepLength = 0.;
  if (step->GetTrack()->GetDefinition()->GetPDGCharge() != 0.) {
    stepLength = step->GetStepLength();
  }

  G4bool noAbsorvedor = (volume == fDetConstruction->GetAbsorberPV());
  G4bool noGap = (volume == fDetConstruction->GetGapPV());

  if (noAbsorvedor) {
    fEventAction->AddAbs(edep, stepLength);
  }

  if (noGap) {
    fEventAction->AddGap(edep, stepLength);
  }

  // [lista_geant4] um registro por passo com deposicao de energia, so dentro do calorimetro
  // (absorvedor ou gap, onde a hierarquia e World > Calorimeter > Layer > Abso/Gap)
  if (edep <= 0. || !(noAbsorvedor || noGap)) return;

  auto touchable = step->GetPreStepPoint()->GetTouchable();
  auto layer = touchable->GetReplicaNumber(1);  // replica da "Layer" (mae do Abso/Gap), 0..9
  auto pos = step->GetPreStepPoint()->GetPosition();
  auto eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();

  auto am = G4AnalysisManager::Instance();
  const G4int id = 1;  // ntuple "CaloHits"
  am->FillNtupleDColumn(id, 0, edep / MeV);
  am->FillNtupleIColumn(id, 1, layer);
  am->FillNtupleDColumn(id, 2, pos.x() / mm);
  am->FillNtupleDColumn(id, 3, pos.y() / mm);
  am->FillNtupleDColumn(id, 4, pos.z() / mm);
  am->FillNtupleIColumn(id, 5, eventID);
  am->FillNtupleIColumn(id, 6, noGap ? 1 : 0);
  am->AddNtupleRow(id);
}

//....oooOO0OOooo........oooOO0OOooo........oooOO0OOooo........oooOO0OOooo......

}  // namespace B4a
