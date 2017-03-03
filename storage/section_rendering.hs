module Main where

main = error "not impl"

type Header = String

--
-- Targets
--

type TargetComponent = String

data TargetInfo = TargetInfo {
  tiHeader :: Header,
  tiComponents :: [TargetComponent]
  }

data TargetInfoNode = TargetInfoNode {
  tinRoot :: TargetInfo,
    tinChildren :: [TargetInfoNode]
  }

leaf_target_info_node :: TargetInfo -> TargetInfoNode
leaf_target_info_node ti = TargetInfoNode ti []

data TargetInfoFactory = TargetInfoFactory [TargetComponent]


sub_factory :: TargetComponent -> TargetInfoFactory -> TargetInfoFactory
sub_factory comp (TargetInfoFactory comps) = TargetInfoFactory (comps ++ [comp])

root_target_info :: Header -> TargetInfoFactory -> TargetInfo
root_target_info header (TargetInfoFactory comps) = TargetInfo header comps

--
-- Section and text
--

data Paragraphs = Paragraphs

data SectionContents = SectionContents {
  initialParagraphs :: Paragraphs,
  subSections       :: [Section]
  }

data Section = Section {
  sectionHeader   :: Header,
  sectionContents :: SectionContents
  }

--
-- Section rendering
--

data RenderingEnvironment

type SectionContentsRenderer = RenderingEnvironment -> SectionContents
type SectionRenderer         = RenderingEnvironment -> Section

constSection :: String -> SectionContentsRenderer
constSection text = \re -> SectionContents Paragraphs []

--
-- Generation node
--

data SectionRendererNode = SectionRendererNode {
  nodeTargetInfoNode   :: TargetInfoNode,
  nodeSectionRenderer  :: SectionRenderer
  }

type SectionGenerator = TargetInfoFactory -> SectionRendererNode

leaf :: (Header, SectionContentsRenderer) -> SectionGenerator
leaf (header, scr) tif = SectionRendererNode
                         (leaf_target_info_node (root_target_info header tif))
                         (\re -> Section header (scr re))


with_sub_sections :: (Header, [(TargetComponent, SectionGenerator)]) -> SectionGenerator
with_sub_sections (header, targetComp_subSectionGenerators) tif =
  SectionRendererNode ti_node section_renderer
  where
    root_ti          :: TargetInfo
    root_ti          = root_target_info header tif
    subSectionNodes  :: [SectionRendererNode]
    subSectionNodes  = [sg (sub_factory tc tif) | (tc, sg) <- targetComp_subSectionGenerators]
    sub_ti_list      :: [TargetInfoNode]
    sub_ti_list      = map nodeTargetInfoNode subSectionNodes
    ti_node          = TargetInfoNode root_ti sub_ti_list
    section_renderer :: SectionRenderer
    section_renderer = \re -> Section header (SectionContents Paragraphs (sub_sections re))
    sub_sections     :: RenderingEnvironment -> [Section]
    sub_sections re  = [nodeSectionRenderer sr re | sr <- subSectionNodes]


doc = with_sub_sections ("Rembrandts", [
  ("skra", leaf ("Skrået", constSection "i rött")),
  ("messias", with_sub_sections
              ("Messias",
	       [("messias2", leaf ("Messias2", constSection "i rött2"))]))
  ])


