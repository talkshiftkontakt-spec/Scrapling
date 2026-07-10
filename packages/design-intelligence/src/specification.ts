export interface DesignSpecification {
  visual_direction: string;
  typography_system: string;
  colour_system: string;
  spacing_system: string;
  layout_system: string;
  component_rules: string[];
  interaction_rules: string[];
  animation_rules: string[];
  inspiration_references: string[];
}

export class DesignSpecificationService {
  public generate(productIdea: string, references: string[]): DesignSpecification {
    return {
      visual_direction: `Create a premium, differentiated ${productIdea} interface inspired by elite references rather than generic SaaS defaults.`,
      typography_system: "Use a restrained sans-serif system with strong hierarchy and compact supporting text.",
      colour_system: "Use a limited premium palette with one sharp accent and calm neutrals.",
      spacing_system: "Adopt a spacious 8pt-based rhythm with deliberate negative space around hero and pricing areas.",
      layout_system: "Blend editorial composition with product-led sections and confident asymmetric moments.",
      component_rules: [
        "Heroes should establish brand confidence within one viewport.",
        "Pricing sections should feel curated, not template-derived.",
        "Dashboards should use clear hierarchy and restrained chrome."
      ],
      interaction_rules: [
        "Prioritize clarity over motion.",
        "Use interaction to reinforce hierarchy, not decorate weak layouts."
      ],
      animation_rules: [
        "Keep motion subtle and structural.",
        "Avoid ornamental animation unrelated to task flow."
      ],
      inspiration_references: references
    };
  }
}
